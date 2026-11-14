package main

import (
	"context"
	"crypto/rand"
	"encoding/hex"
	"flag"
	"fmt"
	"log"
	"net"
	"net/http"
	"os"
	"os/signal"
	"path/filepath"
	"strings"
	"syscall"
	"time"

	"accountpool/internal/pool"
	"accountpool/internal/server"
	"accountpool/internal/store"
)

const version = "0.3.0"

func main() {
	var (
		dataDir    = flag.String("data", "./data", "数据目录")
		adminAddr  = flag.String("admin-addr", "127.0.0.1:18901", "管理 API 监听地址")
		lanAddr    = flag.String("lan-addr", "127.0.0.1:18900", "LAN API 监听地址")
		adminToken = flag.String("admin-token", "", "管理令牌；为空时读取/生成 data/admin.token")
		showVer    = flag.Bool("version", false, "显示版本")
	)
	flag.Parse()
	if *showVer {
		fmt.Println(version)
		return
	}
	if err := os.MkdirAll(*dataDir, 0o700); err != nil {
		log.Fatal(err)
	}
	st, err := store.Open(*dataDir)
	if err != nil {
		log.Fatal(err)
	}
	token := strings.TrimSpace(*adminToken)
	if token == "" {
		token = strings.TrimSpace(os.Getenv("ACCOUNT_POOL_ADMIN_TOKEN"))
	}
	if token == "" {
		token, err = loadOrCreateToken(filepath.Join(*dataDir, "admin.token"))
		if err != nil {
			log.Fatal(err)
		}
	}
	s := server.New(st, pool.New(st), token, *lanAddr, version)

	admin := &http.Server{
		Addr:              *adminAddr,
		Handler:           s.AdminHandler(),
		ReadHeaderTimeout: 10 * time.Second,
	}
	lan := &http.Server{
		Addr:              *lanAddr,
		Handler:           s.LANHandler(),
		ReadHeaderTimeout: 10 * time.Second,
	}
	if !isLoopbackAddr(*adminAddr) {
		log.Printf("警告: 管理 API 未绑定回环地址: %s", *adminAddr)
	}
	log.Printf("accountpool-gateway %s admin=%s lan=%s data=%s", version, *adminAddr, *lanAddr, *dataDir)

	errCh := make(chan error, 2)
	go func() { errCh <- admin.ListenAndServe() }()
	go func() { errCh <- lan.ListenAndServe() }()

	stop := make(chan os.Signal, 1)
	signal.Notify(stop, syscall.SIGINT, syscall.SIGTERM)
	select {
	case sig := <-stop:
		log.Printf("收到信号 %s，正在退出", sig)
	case err := <-errCh:
		if err != nil && err != http.ErrServerClosed {
			log.Printf("服务退出: %v", err)
		}
	}
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	_ = admin.Shutdown(ctx)
	_ = lan.Shutdown(ctx)
}

func isLoopbackAddr(addr string) bool {
	host, _, err := net.SplitHostPort(addr)
	if err != nil {
		return false
	}
	if host == "localhost" {
		return true
	}
	ip := net.ParseIP(host)
	return ip != nil && ip.IsLoopback()
}

func loadOrCreateToken(path string) (string, error) {
	if raw, err := os.ReadFile(path); err == nil {
		if v := strings.TrimSpace(string(raw)); v != "" {
			return v, nil
		}
	}
	b := make([]byte, 24)
	if _, err := rand.Read(b); err != nil {
		return "", err
	}
	token := "adm_" + hex.EncodeToString(b)
	if err := os.WriteFile(path, []byte(token), 0o600); err != nil {
		return "", err
	}
	return token, nil
}
