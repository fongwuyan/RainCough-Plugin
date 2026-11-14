package server

import (
	"crypto/rand"
	"encoding/hex"
	"encoding/json"
	"errors"
	"io"
	"net/http"
	"net/url"
	"strings"

	"accountpool/internal/model"
	"accountpool/internal/pool"
	"accountpool/internal/store"
)

type Server struct {
	Store      *store.Store
	Pool       *pool.Pool
	AdminToken string
	LANAddr    string
	Version    string
	Client     *http.Client
	rpm        map[string]*rpmWindow
}

type rpmWindow struct {
	minute int64
	count  int
}

func New(s *store.Store, p *pool.Pool, adminToken, lanAddr, version string) *Server {
	return &Server{
		Store:      s,
		Pool:       p,
		AdminToken: adminToken,
		LANAddr:    lanAddr,
		Version:    version,
		Client:     &http.Client{Transport: http.DefaultTransport.(*http.Transport).Clone()},
		rpm:        map[string]*rpmWindow{},
	}
}

func (s *Server) AdminHandler() http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("/admin/v1/status", s.admin(s.status))
	mux.HandleFunc("/admin/v1/providers", s.admin(s.providers))
	mux.HandleFunc("/admin/v1/providers/", s.admin(s.providerItem))
	mux.HandleFunc("/admin/v1/accounts", s.admin(s.accounts))
	mux.HandleFunc("/admin/v1/accounts/", s.admin(s.accountItem))
	mux.HandleFunc("/admin/v1/models", s.admin(s.models))
	mux.HandleFunc("/admin/v1/tokens", s.admin(s.tokens))
	mux.HandleFunc("/admin/v1/tokens/", s.admin(s.tokenItem))
	mux.HandleFunc("/admin/v1/usage", s.admin(s.usage))
	return mux
}

func (s *Server) admin(next http.HandlerFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		got := strings.TrimSpace(strings.TrimPrefix(r.Header.Get("Authorization"), "Bearer "))
		if got == "" {
			got = r.Header.Get("X-Admin-Token")
		}
		if s.AdminToken == "" || !constEq(got, s.AdminToken) {
			writeErr(w, http.StatusUnauthorized, "管理员令牌无效")
			return
		}
		next(w, r)
	}
}

func (s *Server) status(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		writeErr(w, http.StatusMethodNotAllowed, "method not allowed")
		return
	}
	d := s.Store.Snapshot()
	active := 0
	for _, a := range d.Accounts {
		if a.Enabled && a.Status != "disabled" && a.CooldownUntil <= model.Now() {
			active++
		}
	}
	writeJSON(w, http.StatusOK, map[string]interface{}{
		"ok": true, "version": s.Version, "lan_addr": s.LANAddr,
		"providers": len(d.Providers), "accounts": len(d.Accounts),
		"active_accounts": active, "tokens": len(d.Tokens), "usage": len(d.Usage),
	})
}

type providerIn struct {
	ID      string   `json:"id"`
	Name    string   `json:"name"`
	Type    string   `json:"type"`
	BaseURL string   `json:"base_url"`
	APIKey  string   `json:"api_key"`
	Models  []string `json:"models"`
	Enabled *bool    `json:"enabled"`
}

func (s *Server) providers(w http.ResponseWriter, r *http.Request) {
	switch r.Method {
	case http.MethodGet:
		d := s.Store.Snapshot()
		out := make([]map[string]interface{}, 0, len(d.Providers))
		for _, p := range d.Providers {
			out = append(out, viewProvider(p))
		}
		writeJSON(w, http.StatusOK, map[string]interface{}{"providers": out})
	case http.MethodPost:
		var in providerIn
		if err := decode(r, &in); err != nil {
			writeErr(w, http.StatusBadRequest, err.Error())
			return
		}
		if in.Name == "" || in.Type == "" || in.BaseURL == "" {
			writeErr(w, http.StatusBadRequest, "name/type/base_url 必填")
			return
		}
		if err := validBaseURL(in.BaseURL); err != nil {
			writeErr(w, http.StatusBadRequest, err.Error())
			return
		}
		var out model.Provider
		err := s.Store.Update(func(d *model.Data) error {
			idx := -1
			for i := range d.Providers {
				if d.Providers[i].ID == in.ID {
					idx = i
					break
				}
			}
			if idx < 0 {
				in.ID = newID("prv")
				d.Providers = append(d.Providers, model.Provider{
					ID: in.ID, CreatedAt: model.Now(), Enabled: true,
				})
				idx = len(d.Providers) - 1
			}
			p := &d.Providers[idx]
			p.Name, p.Type, p.BaseURL = in.Name, in.Type, strings.TrimRight(in.BaseURL, "/")
			if in.Models != nil {
				p.Models = in.Models
			}
			if in.Enabled != nil {
				p.Enabled = *in.Enabled
			}
			if in.APIKey != "" {
				enc, err := s.Store.Vault.Encrypt(in.APIKey)
				if err != nil {
					return err
				}
				p.APIKeyEnc = enc
			}
			p.UpdatedAt = model.Now()
			out = *p
			return nil
		})
		if err != nil {
			writeErr(w, http.StatusInternalServerError, err.Error())
			return
		}
		writeJSON(w, http.StatusOK, map[string]interface{}{"provider": viewProvider(out)})
	default:
		writeErr(w, http.StatusMethodNotAllowed, "method not allowed")
	}
}

func (s *Server) providerItem(w http.ResponseWriter, r *http.Request) {
	rest := strings.TrimPrefix(r.URL.Path, "/admin/v1/providers/")
	parts := strings.Split(strings.Trim(rest, "/"), "/")
	if len(parts) == 2 && parts[1] == "sync" && r.Method == http.MethodPost {
		s.syncProvider(w, parts[0])
		return
	}
	if len(parts) == 1 && r.Method == http.MethodDelete {
		id := parts[0]
		err := s.Store.Update(func(d *model.Data) error {
			for i := range d.Providers {
				if d.Providers[i].ID == id {
					d.Providers = append(d.Providers[:i], d.Providers[i+1:]...)
					return nil
				}
			}
			return errors.New("provider 不存在")
		})
		if err != nil {
			writeErr(w, http.StatusNotFound, err.Error())
			return
		}
		writeJSON(w, http.StatusOK, map[string]interface{}{"ok": true})
		return
	}
	writeErr(w, http.StatusNotFound, "not found")
}

func (s *Server) syncProvider(w http.ResponseWriter, id string) {
	d := s.Store.Snapshot()
	var target *model.Provider
	for i := range d.Providers {
		if d.Providers[i].ID == id {
			target = &d.Providers[i]
			break
		}
	}
	if target == nil {
		writeErr(w, http.StatusNotFound, "provider 不存在")
		return
	}
	key, _ := s.Store.Vault.Decrypt(target.APIKeyEnc)
	if key == "" {
		for _, a := range d.Accounts {
			if a.ProviderID == id && a.KeyEnc != "" {
				key, _ = s.Store.Vault.Decrypt(a.KeyEnc)
				if key != "" {
					break
				}
			}
		}
	}

	var req *http.Request
	var err error
	switch target.Type {
	case "anthropic":
		req, err = http.NewRequest(http.MethodGet, strings.TrimRight(target.BaseURL, "/")+"/v1/models", nil)
		if err == nil {
			req.Header.Set("x-api-key", key)
			req.Header.Set("anthropic-version", "2023-06-01")
		}
	case "gemini":
		req, err = http.NewRequest(http.MethodGet,
			strings.TrimRight(target.BaseURL, "/")+"/v1beta/models?key="+url.QueryEscape(key), nil)
	case "ollama":
		req, err = http.NewRequest(http.MethodGet, strings.TrimRight(target.BaseURL, "/")+"/api/tags", nil)
		if err == nil && key != "" {
			req.Header.Set("Authorization", "Bearer "+key)
		}
	default:
		req, err = http.NewRequest(http.MethodGet, modelsURL(target.BaseURL), nil)
		if err == nil && key != "" {
			req.Header.Set("Authorization", "Bearer "+key)
		}
	}
	if err != nil {
		writeErr(w, http.StatusBadRequest, err.Error())
		return
	}
	resp, err := s.Client.Do(req)
	if err != nil {
		writeErr(w, http.StatusBadGateway, err.Error())
		return
	}
	defer resp.Body.Close()
	body, _ := io.ReadAll(io.LimitReader(resp.Body, 2<<20))
	if resp.StatusCode >= 400 {
		writeErr(w, http.StatusBadGateway, strings.TrimSpace(string(body)))
		return
	}
	list := parseModelList(target.Type, body)
	if len(list) == 0 {
		writeErr(w, http.StatusBadGateway, "上游没有返回可解析的模型列表")
		return
	}
	_ = s.Store.Update(func(data *model.Data) error {
		for i := range data.Providers {
			if data.Providers[i].ID == id {
				data.Providers[i].Models = list
				data.Providers[i].UpdatedAt = model.Now()
			}
		}
		return nil
	})
	writeJSON(w, http.StatusOK, map[string]interface{}{"ok": true, "models": list})
}

func parseModelList(typ string, body []byte) []string {
	var list []string
	switch typ {
	case "gemini":
		var out struct {
			Models []struct {
				Name string `json:"name"`
			} `json:"models"`
		}
		if json.Unmarshal(body, &out) == nil {
			for _, m := range out.Models {
				list = append(list, strings.TrimPrefix(m.Name, "models/"))
			}
		}
	case "ollama":
		var out struct {
			Models []struct {
				Name string `json:"name"`
			} `json:"models"`
		}
		if json.Unmarshal(body, &out) == nil {
			for _, m := range out.Models {
				list = append(list, m.Name)
			}
		}
	default:
		var out struct {
			Data []struct {
				ID string `json:"id"`
			} `json:"data"`
		}
		if json.Unmarshal(body, &out) == nil {
			for _, m := range out.Data {
				list = append(list, m.ID)
			}
		}
	}
	return list
}

type accountIn struct {
	ID             string `json:"id"`
	ProviderID     string `json:"provider_id"`
	Label          string `json:"label"`
	APIKey         string `json:"api_key"`
	Weight         int    `json:"weight"`
	Priority       int    `json:"priority"`
	MaxConcurrency int    `json:"max_concurrency"`
	Enabled        *bool  `json:"enabled"`
}

func (s *Server) accounts(w http.ResponseWriter, r *http.Request) {
	switch r.Method {
	case http.MethodGet:
		d := s.Store.Snapshot()
		out := make([]map[string]interface{}, 0, len(d.Accounts))
		for _, a := range d.Accounts {
			out = append(out, viewAccount(a))
		}
		writeJSON(w, http.StatusOK, map[string]interface{}{"accounts": out})
	case http.MethodPost:
		var in accountIn
		if err := decode(r, &in); err != nil {
			writeErr(w, http.StatusBadRequest, err.Error())
			return
		}
		if in.ProviderID == "" || in.Label == "" {
			writeErr(w, http.StatusBadRequest, "provider_id/label 必填")
			return
		}
		d := s.Store.Snapshot()
		found := false
		for _, p := range d.Providers {
			if p.ID == in.ProviderID {
				found = true
			}
		}
		if !found {
			writeErr(w, http.StatusBadRequest, "provider 不存在")
			return
		}
		enc := ""
		if in.APIKey != "" {
			var err error
			enc, err = s.Store.Vault.Encrypt(in.APIKey)
			if err != nil {
				writeErr(w, http.StatusInternalServerError, err.Error())
				return
			}
		}
		var out model.Account
		err := s.Store.Update(func(data *model.Data) error {
			idx := -1
			for i := range data.Accounts {
				if data.Accounts[i].ID == in.ID {
					idx = i
					break
				}
			}
			if idx < 0 {
				in.ID = newID("acc")
				data.Accounts = append(data.Accounts, model.Account{
					ID: in.ID, CreatedAt: model.Now(), Enabled: true,
				})
				idx = len(data.Accounts) - 1
			}
			a := &data.Accounts[idx]
			a.ProviderID, a.Label = in.ProviderID, in.Label
			if in.Weight > 0 {
				a.Weight = in.Weight
			} else if a.Weight == 0 {
				a.Weight = 1
			}
			a.Priority = in.Priority
			if in.MaxConcurrency > 0 {
				a.MaxConcurrency = in.MaxConcurrency
			}
			if in.Enabled != nil {
				a.Enabled = *in.Enabled
			}
			if enc != "" {
				a.KeyEnc = enc
			}
			a.Status = "unknown"
			a.CooldownUntil = 0
			a.LastError = ""
			a.UpdatedAt = model.Now()
			out = *a
			return nil
		})
		if err != nil {
			writeErr(w, http.StatusInternalServerError, err.Error())
			return
		}
		writeJSON(w, http.StatusOK, map[string]interface{}{"account": viewAccount(out)})
	default:
		writeErr(w, http.StatusMethodNotAllowed, "method not allowed")
	}
}

func (s *Server) accountItem(w http.ResponseWriter, r *http.Request) {
	id := strings.Trim(strings.TrimPrefix(r.URL.Path, "/admin/v1/accounts/"), "/")
	if id == "" {
		writeErr(w, http.StatusNotFound, "not found")
		return
	}
	if r.Method == http.MethodDelete {
		err := s.Store.Update(func(d *model.Data) error {
			for i := range d.Accounts {
				if d.Accounts[i].ID == id {
					d.Accounts = append(d.Accounts[:i], d.Accounts[i+1:]...)
					return nil
				}
			}
			return errors.New("account 不存在")
		})
		if err != nil {
			writeErr(w, http.StatusNotFound, err.Error())
			return
		}
		writeJSON(w, http.StatusOK, map[string]interface{}{"ok": true})
		return
	}
	writeErr(w, http.StatusNotFound, "not found")
}

func (s *Server) models(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		writeErr(w, http.StatusMethodNotAllowed, "method not allowed")
		return
	}
	d := s.Store.Snapshot()
	seen := map[string]bool{}
	out := make([]map[string]interface{}, 0)
	for _, p := range d.Providers {
		if !p.Enabled {
			continue
		}
		for _, m := range p.Models {
			if m == "" || seen[m] {
				continue
			}
			seen[m] = true
			out = append(out, map[string]interface{}{"id": m, "provider_id": p.ID, "provider": p.Name})
		}
	}
	writeJSON(w, http.StatusOK, map[string]interface{}{"models": out})
}

type tokenIn struct {
	Name          string   `json:"name"`
	AllowedModels []string `json:"allowed_models"`
	RPM           int      `json:"rpm"`
	DailyQuota    int      `json:"daily_quota"`
	IPAllow       []string `json:"ip_allow"`
	ExpiresAt     int64    `json:"expires_at"`
}

func (s *Server) tokens(w http.ResponseWriter, r *http.Request) {
	switch r.Method {
	case http.MethodGet:
		d := s.Store.Snapshot()
		out := make([]map[string]interface{}, 0, len(d.Tokens))
		for _, t := range d.Tokens {
			out = append(out, viewToken(t))
		}
		writeJSON(w, http.StatusOK, map[string]interface{}{"tokens": out})
	case http.MethodPost:
		var in tokenIn
		if err := decode(r, &in); err != nil {
			writeErr(w, http.StatusBadRequest, err.Error())
			return
		}
		if strings.TrimSpace(in.Name) == "" {
			writeErr(w, http.StatusBadRequest, "name 必填")
			return
		}
		plain, hash, err := newToken()
		if err != nil {
			writeErr(w, http.StatusInternalServerError, err.Error())
			return
		}
		t := model.Token{
			ID: newID("tok"), Name: in.Name, Hash: hash,
			AllowedModels: in.AllowedModels, RPM: in.RPM, DailyQuota: in.DailyQuota,
			IPAllow: in.IPAllow, ExpiresAt: in.ExpiresAt, Enabled: true,
			UsedDay: model.Today(), CreatedAt: model.Now(), UpdatedAt: model.Now(),
		}
		if err := s.Store.Update(func(d *model.Data) error {
			d.Tokens = append(d.Tokens, t)
			return nil
		}); err != nil {
			writeErr(w, http.StatusInternalServerError, err.Error())
			return
		}
		writeJSON(w, http.StatusOK, map[string]interface{}{"token": plain, "info": viewToken(t)})
	default:
		writeErr(w, http.StatusMethodNotAllowed, "method not allowed")
	}
}

func (s *Server) tokenItem(w http.ResponseWriter, r *http.Request) {
	rest := strings.Trim(strings.TrimPrefix(r.URL.Path, "/admin/v1/tokens/"), "/")
	parts := strings.Split(rest, "/")
	if len(parts) == 1 && r.Method == http.MethodDelete {
		id := parts[0]
		_ = s.Store.Update(func(d *model.Data) error {
			for i := range d.Tokens {
				if d.Tokens[i].ID == id {
					d.Tokens[i].Enabled = false
					d.Tokens[i].UpdatedAt = model.Now()
				}
			}
			return nil
		})
		writeJSON(w, http.StatusOK, map[string]interface{}{"ok": true})
		return
	}
	writeErr(w, http.StatusNotFound, "not found")
}

func (s *Server) usage(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		writeErr(w, http.StatusMethodNotAllowed, "method not allowed")
		return
	}
	d := s.Store.Snapshot()
	limit := 100
	if v := r.URL.Query().Get("limit"); v != "" {
		if n, err := parseInt(v); err == nil && n > 0 {
			limit = n
		}
	}
	if limit > 1000 {
		limit = 1000
	}
	out := d.Usage
	if len(out) > limit {
		out = out[len(out)-limit:]
	}
	writeJSON(w, http.StatusOK, map[string]interface{}{"usage": out})
}

func viewProvider(p model.Provider) map[string]interface{} {
	return map[string]interface{}{
		"id": p.ID, "name": p.Name, "type": p.Type, "base_url": p.BaseURL,
		"models": p.Models, "enabled": p.Enabled, "has_key": p.APIKeyEnc != "",
		"created_at": p.CreatedAt, "updated_at": p.UpdatedAt,
	}
}

func viewAccount(a model.Account) map[string]interface{} {
	return map[string]interface{}{
		"id": a.ID, "provider_id": a.ProviderID, "label": a.Label,
		"weight": a.Weight, "priority": a.Priority, "max_concurrency": a.MaxConcurrency,
		"enabled": a.Enabled, "status": a.Status, "cooldown_until": a.CooldownUntil,
		"last_error": a.LastError, "last_used": a.LastUsed, "has_key": a.KeyEnc != "",
		"created_at": a.CreatedAt, "updated_at": a.UpdatedAt,
	}
}

func viewToken(t model.Token) map[string]interface{} {
	return map[string]interface{}{
		"id": t.ID, "name": t.Name, "allowed_models": t.AllowedModels,
		"rpm": t.RPM, "daily_quota": t.DailyQuota, "ip_allow": t.IPAllow,
		"expires_at": t.ExpiresAt, "enabled": t.Enabled,
		"used_day": t.UsedDay, "used_count": t.UsedCount,
		"created_at": t.CreatedAt, "updated_at": t.UpdatedAt,
	}
}

func writeJSON(w http.ResponseWriter, code int, v interface{}) {
	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	w.WriteHeader(code)
	_ = json.NewEncoder(w).Encode(v)
}

func writeErr(w http.ResponseWriter, code int, msg string) {
	writeJSON(w, code, map[string]interface{}{"error": msg})
}

func decode(r *http.Request, v interface{}) error {
	defer r.Body.Close()
	dec := json.NewDecoder(io.LimitReader(r.Body, 2<<20))
	return dec.Decode(v)
}

func newID(prefix string) string {
	b := make([]byte, 5)
	_, _ = rand.Read(b)
	return prefix + "_" + hex.EncodeToString(b)
}

func newToken() (string, string, error) {
	b := make([]byte, 24)
	if _, err := rand.Read(b); err != nil {
		return "", "", err
	}
	plain := "ap_" + hex.EncodeToString(b)
	return plain, hashToken(plain), nil
}

func validBaseURL(raw string) error {
	u, err := url.Parse(raw)
	if err != nil || (u.Scheme != "http" && u.Scheme != "https") || u.Host == "" {
		return errors.New("base_url 必须是 http/https 地址")
	}
	return nil
}

func parseInt(v string) (int, error) {
	n := 0
	for _, c := range v {
		if c < '0' || c > '9' {
			return 0, errors.New("not int")
		}
		n = n*10 + int(c-'0')
	}
	return n, nil
}
