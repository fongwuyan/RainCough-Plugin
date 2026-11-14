$ErrorActionPreference = 'Stop'
Set-Location (Join-Path $PSScriptRoot 'gateway')
New-Item -ItemType Directory -Force ..\bin\windows-amd64 | Out-Null
$env:GOOS='windows'; $env:GOARCH='amd64'; $env:CGO_ENABLED='0'
go build -trimpath -ldflags "-s -w" -o ..\bin\windows-amd64\accountpool-gateway.exe .
Write-Host 'built windows binary'
