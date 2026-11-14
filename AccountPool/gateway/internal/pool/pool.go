package pool

import (
	"errors"
	"strings"
	"sync"

	"accountpool/internal/model"
	"accountpool/internal/store"
)

type Selection struct {
	Account  model.Account
	Provider model.Provider
	Key      string
}

type Pool struct {
	store *store.Store
	mu    sync.Mutex
	rr    map[string]int
	load  map[string]int
}

func New(s *store.Store) *Pool {
	return &Pool{store: s, rr: map[string]int{}, load: map[string]int{}}
}

func (p *Pool) Select(modelName string, exclude map[string]bool, types ...string) (*Selection, error) {
	snap := p.store.Snapshot()
	now := model.Now()

	providers := make(map[string]model.Provider, len(snap.Providers))
	for _, pr := range snap.Providers {
		if pr.Enabled {
			providers[pr.ID] = pr
		}
	}

	candidates := make([]Selection, 0)
	for _, acc := range snap.Accounts {
		if !acc.Enabled || acc.Status == "disabled" || exclude[acc.ID] {
			continue
		}
		if acc.CooldownUntil > now {
			continue
		}
		pr, ok := providers[acc.ProviderID]
		if !ok {
			continue
		}
		if len(pr.Models) > 0 && !contains(pr.Models, modelName) {
			continue
		}
		if len(types) > 0 && !contains(types, pr.Type) {
			continue
		}
		if acc.KeyEnc == "" {
			continue
		}
		key, err := p.store.Vault.Decrypt(acc.KeyEnc)
		if err != nil || key == "" {
			continue
		}
		candidates = append(candidates, Selection{Account: acc, Provider: pr, Key: key})
	}
	if len(candidates) == 0 {
		return nil, errors.New("没有可用账号")
	}

	p.mu.Lock()
	defer p.mu.Unlock()
	best := candidates[0]
	bestScore := -1
	for _, c := range candidates {
		load := p.load[c.Account.ID]
		if c.Account.MaxConcurrency > 0 && load >= c.Account.MaxConcurrency {
			continue
		}
		score := c.Account.Priority*1000 + c.Account.Weight*10 - load
		if score > bestScore {
			bestScore = score
			best = c
		}
	}
	if bestScore < 0 {
		return nil, errors.New("账号并发已满")
	}
	p.load[best.Account.ID]++
	return &best, nil
}

func (p *Pool) Release(accountID string) {
	p.mu.Lock()
	if p.load[accountID] > 0 {
		p.load[accountID]--
	}
	p.mu.Unlock()
}

func (p *Pool) Cooldown(accountID string, seconds int64, msg string) {
	_ = p.store.Update(func(d *model.Data) error {
		for i := range d.Accounts {
			if d.Accounts[i].ID == accountID {
				d.Accounts[i].Status = "cooldown"
				d.Accounts[i].CooldownUntil = model.Now() + seconds
				d.Accounts[i].LastError = msg
				d.Accounts[i].UpdatedAt = model.Now()
			}
		}
		return nil
	})
}

func (p *Pool) MarkOK(accountID string) {
	_ = p.store.Update(func(d *model.Data) error {
		for i := range d.Accounts {
			if d.Accounts[i].ID == accountID {
				d.Accounts[i].Status = "ok"
				d.Accounts[i].CooldownUntil = 0
				d.Accounts[i].LastError = ""
				d.Accounts[i].LastUsed = model.Now()
				d.Accounts[i].UpdatedAt = model.Now()
			}
		}
		return nil
	})
}

func contains(list []string, v string) bool {
	for _, x := range list {
		if strings.EqualFold(x, v) {
			return true
		}
	}
	return false
}
