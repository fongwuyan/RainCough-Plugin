#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")/gateway"
mkdir -p ../bin/linux-amd64 ../bin/linux-arm64
GOOS=linux GOARCH=amd64 CGO_ENABLED=0 go build -trimpath -ldflags "-s -w" -o ../bin/linux-amd64/accountpool-gateway .
GOOS=linux GOARCH=arm64 CGO_ENABLED=0 go build -trimpath -ldflags "-s -w" -o ../bin/linux-arm64/accountpool-gateway .
echo "built linux binaries"
