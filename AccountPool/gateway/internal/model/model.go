package model

import "time"

const DataVersion = 1

type Provider struct {
	ID        string   `json:"id"`
	Name      string   `json:"name"`
	Type      string   `json:"type"` // openai, azure, anthropic, gemini, ollama, vllm, custom
	BaseURL   string   `json:"base_url"`
	APIKeyEnc string   `json:"api_key_enc,omitempty"`
	Models    []string `json:"models,omitempty"`
	Enabled   bool     `json:"enabled"`
	CreatedAt int64    `json:"created_at"`
	UpdatedAt int64    `json:"updated_at"`
}

type Account struct {
	ID             string `json:"id"`
	ProviderID     string `json:"provider_id"`
	Label          string `json:"label"`
	KeyEnc         string `json:"key_enc,omitempty"`
	Weight         int    `json:"weight"`
	Priority       int    `json:"priority"`
	MaxConcurrency int    `json:"max_concurrency"`
	Enabled        bool   `json:"enabled"`
	Status         string `json:"status"` // unknown, ok, cooldown, disabled
	CooldownUntil  int64  `json:"cooldown_until"`
	LastError      string `json:"last_error,omitempty"`
	LastUsed       int64  `json:"last_used"`
	CreatedAt      int64  `json:"created_at"`
	UpdatedAt      int64  `json:"updated_at"`
}

type Token struct {
	ID            string   `json:"id"`
	Name          string   `json:"name"`
	Hash          string   `json:"hash"`
	AllowedModels []string `json:"allowed_models,omitempty"`
	RPM           int      `json:"rpm"`
	DailyQuota    int      `json:"daily_quota"`
	IPAllow       []string `json:"ip_allow,omitempty"`
	ExpiresAt     int64    `json:"expires_at"`
	Enabled       bool     `json:"enabled"`
	UsedDay       string   `json:"used_day"`
	UsedCount     int      `json:"used_count"`
	CreatedAt     int64    `json:"created_at"`
	UpdatedAt     int64    `json:"updated_at"`
}

type Usage struct {
	ID               string `json:"id"`
	Time             int64  `json:"time"`
	TokenID          string `json:"token_id"`
	AccountID        string `json:"account_id"`
	ProviderID       string `json:"provider_id"`
	Model            string `json:"model"`
	PromptTokens     int    `json:"prompt_tokens"`
	CompletionTokens int    `json:"completion_tokens"`
	TotalTokens      int    `json:"total_tokens"`
	LatencyMS        int64  `json:"latency_ms"`
	Status           int    `json:"status"`
	Error            string `json:"error,omitempty"`
}

type Data struct {
	Version   int        `json:"version"`
	Providers []Provider `json:"providers"`
	Accounts  []Account  `json:"accounts"`
	Tokens    []Token    `json:"tokens"`
	Usage     []Usage    `json:"usage"`
}

func NewData() Data {
	return Data{Version: DataVersion}
}

func Now() int64 { return time.Now().Unix() }

func Today() string { return time.Now().Format("2006-01-02") }
