# RainCough 号池管理台（AccountPool）

自研的账号 / API Key 池与局域网模型网关，作为 RainCough 插件运行。

- 不包含注册机
- 只管理你已有、且有权使用的账号 / API Key
- Go Gateway 负责转发、账号池、路由、额度
- Python 控制面 + RainCough 管理页面
- Apache-2.0

## 当前版本

`0.1.0`：Gateway 核心、OpenAI 兼容上游、账号池、下游 Token、管理页面。

## 目录

```text
AccountPool/
  gateway/        Go Gateway 源码
  backend/        RainCough Python 控制面
  frontend/       管理页面源码
  assets/         构建后的页面
  bin/            各平台 Gateway 二进制
```

## 构建

```bash
cd gateway
GOOS=linux GOARCH=amd64 CGO_ENABLED=0 go build -trimpath -ldflags "-s -w" \
  -o ../bin/linux-amd64/accountpool-gateway ./...
```

Windows：

```powershell
cd gateway
$env:GOOS='windows'; $env:GOARCH='amd64'; $env:CGO_ENABLED='0'
go build -trimpath -ldflags "-s -w" -o ..\bin\windows-amd64\accountpool-gateway.exe .
```

## 运行逻辑

Python 控制面启动 `accountpool-gateway`：

- 管理 API：`127.0.0.1:18901`
- LAN API：默认 `127.0.0.1:18900`
- 数据目录：插件目录 `data/`
- 凭据 AES-GCM 加密
- 下游 Token 只存 SHA-256

## 安全

- 默认 LAN API 只监听回环
- 打开局域网需要在设置中显式开启
- 不记录完整 Prompt
- 不在页面回显 API Key

## License

Apache-2.0，见 `LICENSE`。
