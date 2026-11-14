package store

import (
	"encoding/json"
	"errors"
	"os"
	"path/filepath"
	"sync"

	"accountpool/internal/model"
)

type Store struct {
	mu    sync.RWMutex
	path  string
	data  model.Data
	Vault *Vault
}

func Open(dir string) (*Store, error) {
	v, err := LoadVault(dir)
	if err != nil {
		return nil, err
	}
	s := &Store{path: filepath.Join(dir, "accountpool.json"), Vault: v, data: model.NewData()}
	raw, err := os.ReadFile(s.path)
	if errors.Is(err, os.ErrNotExist) {
		return s, s.saveLocked()
	}
	if err != nil {
		return nil, err
	}
	if err := json.Unmarshal(raw, &s.data); err != nil {
		return nil, err
	}
	if s.data.Version == 0 {
		s.data.Version = model.DataVersion
	}
	return s, nil
}

func (s *Store) Snapshot() model.Data {
	s.mu.RLock()
	defer s.mu.RUnlock()
	out := s.data
	out.Providers = append([]model.Provider(nil), s.data.Providers...)
	out.Accounts = append([]model.Account(nil), s.data.Accounts...)
	out.Tokens = append([]model.Token(nil), s.data.Tokens...)
	out.Usage = append([]model.Usage(nil), s.data.Usage...)
	return out
}

func (s *Store) Update(fn func(*model.Data) error) error {
	s.mu.Lock()
	defer s.mu.Unlock()
	if err := fn(&s.data); err != nil {
		return err
	}
	return s.saveLocked()
}

func (s *Store) saveLocked() error {
	raw, err := json.MarshalIndent(s.data, "", "  ")
	if err != nil {
		return err
	}
	if err := os.MkdirAll(filepath.Dir(s.path), 0o700); err != nil {
		return err
	}
	tmp := s.path + ".tmp"
	if err := os.WriteFile(tmp, raw, 0o600); err != nil {
		return err
	}
	return os.Rename(tmp, s.path)
}
