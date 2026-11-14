package server

import (
	"bytes"
	"crypto/sha256"
	"crypto/subtle"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net"
	"net/http"
	"strings"
	"time"

	"accountpool/internal/model"
	"accountpool/internal/pool"
)

func (s *Server) LANHandler() http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("/v1/models", s.lanModels)
	mux.HandleFunc("/v1/chat/completions", s.chatCompletions)
	return mux
}

func (s *Server) lanModels(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		writeErr(w, http.StatusMethodNotAllowed, "method not allowed")
		return
	}
	tok, err := s.authenticate(r)
	if err != nil {
		writeErr(w, http.StatusUnauthorized, err.Error())
		return
	}
	d := s.Store.Snapshot()
	seen := map[string]bool{}
	data := make([]map[string]interface{}, 0)
	for _, p := range d.Providers {
		if !p.Enabled {
			continue
		}
		for _, m := range p.Models {
			if m == "" || seen[m] || !tokenAllows(*tok, m) {
				continue
			}
			seen[m] = true
			data = append(data, map[string]interface{}{
				"id": m, "object": "model", "owned_by": p.Name,
			})
		}
	}
	writeJSON(w, http.StatusOK, map[string]interface{}{"object": "list", "data": data})
}

func (s *Server) chatCompletions(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		writeErr(w, http.StatusMethodNotAllowed, "method not allowed")
		return
	}
	body, err := io.ReadAll(io.LimitReader(r.Body, 32<<20))
	if err != nil {
		writeErr(w, http.StatusBadRequest, "读取请求失败")
		return
	}
	var req struct {
		Model  string `json:"model"`
		Stream bool   `json:"stream"`
	}
	if err := json.Unmarshal(body, &req); err != nil || req.Model == "" {
		writeErr(w, http.StatusBadRequest, "model 必填")
		return
	}
	tok, err := s.authenticate(r)
	if err != nil {
		writeErr(w, http.StatusUnauthorized, err.Error())
		return
	}
	if !tokenAllows(*tok, req.Model) {
		writeErr(w, http.StatusForbidden, "该令牌不允许使用此模型")
		return
	}

	start := time.Now()
	failed := map[string]bool{}
	var lastErr string
	for attempt := 0; attempt < 3; attempt++ {
		sel, err := s.Pool.Select(req.Model, failed)
		if err != nil {
			lastErr = err.Error()
			break
		}
		if !isOpenAICompatible(sel.Provider.Type) {
			s.Pool.Release(sel.Account.ID)
			lastErr = "该 Provider 协议尚未实现: " + sel.Provider.Type
			break
		}
		ok := s.tryUpstream(w, r, body, req.Stream, sel, tok, start)
		s.Pool.Release(sel.Account.ID)
		if ok {
			return
		}
		failed[sel.Account.ID] = true
		lastErr = "上游请求失败"
	}
	if lastErr == "" {
		lastErr = "没有可用账号"
	}
	writeErr(w, http.StatusBadGateway, lastErr)
}

func (s *Server) tryUpstream(w http.ResponseWriter, r *http.Request, body []byte, stream bool,
	sel *pool.Selection, tok *model.Token, start time.Time) bool {
	url := chatURL(sel.Provider.BaseURL)
	req, err := http.NewRequestWithContext(r.Context(), http.MethodPost, url, bytes.NewReader(body))
	if err != nil {
		s.Pool.Cooldown(sel.Account.ID, 30, err.Error())
		return false
	}
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+sel.Key)
	req.Header.Set("Accept", "text/event-stream, application/json")
	if v := r.Header.Get("OpenAI-Beta"); v != "" {
		req.Header.Set("OpenAI-Beta", v)
	}
	resp, err := s.Client.Do(req)
	if err != nil {
		s.Pool.Cooldown(sel.Account.ID, 60, trimErr(err.Error()))
		s.record(tok.ID, sel, "", 0, time.Since(start).Milliseconds(), 502, trimErr(err.Error()))
		return false
	}
	defer resp.Body.Close()
	if resp.StatusCode >= 400 {
		msg, _ := io.ReadAll(io.LimitReader(resp.Body, 4096))
		text := strings.TrimSpace(string(msg))
		cooldown := int64(0)
		switch resp.StatusCode {
		case 401, 403:
			cooldown = 300
		case 429:
			cooldown = 60
		default:
			if resp.StatusCode >= 500 {
				cooldown = 30
			}
		}
		if cooldown > 0 {
			s.Pool.Cooldown(sel.Account.ID, cooldown, fmt.Sprintf("HTTP %d", resp.StatusCode))
		}
		s.record(tok.ID, sel, "", 0, time.Since(start).Milliseconds(), resp.StatusCode, text)
		return false
	}

	contentType := resp.Header.Get("Content-Type")
	if stream {
		w.Header().Set("Content-Type", "text/event-stream")
		w.Header().Set("Cache-Control", "no-cache")
		w.Header().Set("Connection", "keep-alive")
		w.WriteHeader(http.StatusOK)
		flusher, _ := w.(http.Flusher)
		buf := make([]byte, 32<<10)
		for {
			n, err := resp.Body.Read(buf)
			if n > 0 {
				if _, werr := w.Write(buf[:n]); werr != nil {
					break
				}
				if flusher != nil {
					flusher.Flush()
				}
			}
			if err != nil {
				break
			}
		}
		s.Pool.MarkOK(sel.Account.ID)
		s.record(tok.ID, sel, "", 0, time.Since(start).Milliseconds(), 200, "")
		return true
	}

	raw, err := io.ReadAll(io.LimitReader(resp.Body, 32<<20))
	if err != nil {
		s.Pool.Cooldown(sel.Account.ID, 30, trimErr(err.Error()))
		return false
	}
	prompt, completion, total := parseUsage(raw)
	if contentType != "" {
		w.Header().Set("Content-Type", contentType)
	}
	w.WriteHeader(resp.StatusCode)
	_, _ = w.Write(raw)
	s.Pool.MarkOK(sel.Account.ID)
	s.recordUsage(tok.ID, sel, reqModel(body), prompt, completion, total, time.Since(start).Milliseconds(), 200, "")
	return true
}

type poolSelection struct {
	Account  model.Account
	Provider model.Provider
	Key      string
}

func (p poolSelection) ModelForUsage() string { return "" }

func (s *Server) authenticate(r *http.Request) (*model.Token, error) {
	auth := strings.TrimSpace(r.Header.Get("Authorization"))
	if !strings.HasPrefix(strings.ToLower(auth), "bearer ") {
		return nil, errors.New("缺少 Bearer Token")
	}
	plain := strings.TrimSpace(auth[7:])
	if plain == "" {
		return nil, errors.New("缺少 Token")
	}
	hash := hashToken(plain)
	d := s.Store.Snapshot()
	now := model.Now()
	ip := clientIP(r)
	var found *model.Token
	for i := range d.Tokens {
		t := &d.Tokens[i]
		if t.Hash != hash || !t.Enabled {
			continue
		}
		if t.ExpiresAt > 0 && t.ExpiresAt < now {
			return nil, errors.New("令牌已过期")
		}
		if len(t.IPAllow) > 0 && !ipAllowed(ip, t.IPAllow) {
			return nil, errors.New("IP 不在白名单")
		}
		found = t
		break
	}
	if found == nil {
		return nil, errors.New("令牌无效")
	}
	today := model.Today()
	if found.UsedDay != today {
		found.UsedDay = today
		found.UsedCount = 0
	}
	if found.DailyQuota > 0 && found.UsedCount >= found.DailyQuota {
		return nil, errors.New("今日额度已用完")
	}
	if found.RPM > 0 && !s.allowRPM(found.ID, found.RPM) {
		return nil, errors.New("请求过于频繁")
	}
	found.UsedCount++
	found.UpdatedAt = now
	_ = s.Store.Update(func(data *model.Data) error {
		for i := range data.Tokens {
			if data.Tokens[i].ID == found.ID {
				data.Tokens[i].UsedDay = found.UsedDay
				data.Tokens[i].UsedCount = found.UsedCount
				data.Tokens[i].UpdatedAt = found.UpdatedAt
			}
		}
		return nil
	})
	return found, nil
}

func (s *Server) allowRPM(tokenID string, limit int) bool {
	minute := time.Now().Unix() / 60
	w := s.rpm[tokenID]
	if w == nil || w.minute != minute {
		s.rpm[tokenID] = &rpmWindow{minute: minute, count: 1}
		return true
	}
	if w.count >= limit {
		return false
	}
	w.count++
	return true
}

func (s *Server) record(tokenID string, sel *pool.Selection, _ string, _, latency int64, status int, errMsg string) {
	s.recordUsage(tokenID, sel, "", 0, 0, 0, latency, status, errMsg)
}

func (s *Server) recordUsage(tokenID string, sel *pool.Selection, modelName string, prompt, completion, total int, latency int64, status int, errMsg string) {
	u := model.Usage{
		ID: newID("use"), Time: model.Now(), TokenID: tokenID,
		AccountID: sel.Account.ID, ProviderID: sel.Provider.ID, Model: modelName,
		PromptTokens: prompt, CompletionTokens: completion, TotalTokens: total,
		LatencyMS: latency, Status: status, Error: errMsg,
	}
	_ = s.Store.Update(func(d *model.Data) error {
		d.Usage = append(d.Usage, u)
		if len(d.Usage) > 5000 {
			d.Usage = d.Usage[len(d.Usage)-5000:]
		}
		return nil
	})
}

func parseUsage(raw []byte) (int, int, int) {
	var v struct {
		Usage struct {
			PromptTokens     int `json:"prompt_tokens"`
			CompletionTokens int `json:"completion_tokens"`
			TotalTokens      int `json:"total_tokens"`
		} `json:"usage"`
	}
	if json.Unmarshal(raw, &v) != nil {
		return 0, 0, 0
	}
	return v.Usage.PromptTokens, v.Usage.CompletionTokens, v.Usage.TotalTokens
}

func reqModel(body []byte) string {
	var v struct {
		Model string `json:"model"`
	}
	_ = json.Unmarshal(body, &v)
	return v.Model
}

func tokenAllows(t model.Token, modelName string) bool {
	if len(t.AllowedModels) == 0 {
		return true
	}
	for _, m := range t.AllowedModels {
		if strings.EqualFold(m, modelName) || m == "*" {
			return true
		}
	}
	return false
}

func ipAllowed(ip string, list []string) bool {
	parsed := net.ParseIP(ip)
	for _, raw := range list {
		raw = strings.TrimSpace(raw)
		if raw == "" {
			continue
		}
		if strings.Contains(raw, "/") {
			_, cidr, err := net.ParseCIDR(raw)
			if err == nil && parsed != nil && cidr.Contains(parsed) {
				return true
			}
			continue
		}
		if raw == ip {
			return true
		}
	}
	return false
}

func clientIP(r *http.Request) string {
	host, _, err := net.SplitHostPort(r.RemoteAddr)
	if err != nil {
		return r.RemoteAddr
	}
	return host
}

func hashToken(plain string) string {
	sum := sha256.Sum256([]byte(plain))
	return hex.EncodeToString(sum[:])
}

func constEq(a, b string) bool {
	if len(a) != len(b) {
		return false
	}
	return subtle.ConstantTimeCompare([]byte(a), []byte(b)) == 1
}

func isOpenAICompatible(t string) bool {
	switch t {
	case "openai", "azure", "ollama", "vllm", "custom", "deepseek", "zhipu", "moonshot", "qwen":
		return true
	default:
		return false
	}
}

func chatURL(base string) string {
	b := strings.TrimRight(base, "/")
	if strings.HasSuffix(b, "/chat/completions") {
		return b
	}
	if strings.HasSuffix(b, "/v1") {
		return b + "/chat/completions"
	}
	return b + "/v1/chat/completions"
}

func modelsURL(base string) string {
	b := strings.TrimRight(base, "/")
	if strings.HasSuffix(b, "/models") {
		return b
	}
	if strings.HasSuffix(b, "/v1") {
		return b + "/models"
	}
	return b + "/v1/models"
}

func trimErr(s string) string {
	if len(s) > 200 {
		return s[:200]
	}
	return s
}
