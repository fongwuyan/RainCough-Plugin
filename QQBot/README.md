# QQBot 插件

SnowLuma（Docker 协议端）+ rcbot（机器人本体）的统一控制台。

**接手先读 [`docs/QQ-Bot-接手文档.md`](../../docs/QQ-Bot-接手文档.md)** —— 架构、部署、
配置、接口、排查手册、踩过的坑都在那儿。

> 2026-11-07 起插件只支持 SnowLuma。NapCat 后端（WebUI 客户端、systemd 多实例、
> 二维码登录、后端切换）已整体移除。

## 目录

| 路径 | 说明 |
|---|---|
| `plugin.json` | 插件清单（接口声明 + 环境预检），`version` 要和 `VERSION`、`server_v4.py` 三处一致 |
| `server_v4.py` | 插件后端：SnowLuma / rcbot 的转发与聚合，不持有业务状态 |
| `frontend/plugin.js` + `frontend/im/` | 前端源码（Vue 3），消息页是整屏 overlay |
| `assets/plugin.js` | **构建产物**，面板实际加载这个，改源码后必须重新构建 |
| `rcbot/` `rcbot.py` | 机器人本体源码，部署到 `/opt/rcbot`，由 `rcbot.service` 跑 |
| `rcbot/slstatus.py` | `#sl` 指令的状态摘要（容器 / 登录 / OneBot / 档案） |
| `tools/deploy.py` | 一键部署（走面板 HTTP，不需要 SSH） |
| `data/config.json` | 插件自己的连接配置（rcbot 地址、超时） |

## 端口

| 用途 | 端口 |
|---|---|
| SnowLuma WebUI | 5099 |
| noVNC 远程桌面（扫码登录） | 6081 |
| OneBot HTTP | 3000 |
| OneBot WebSocket（rcbot 连它） | 3001 |
| rcbot HTTP | 6710 |

`onebot*.json` 里 `reportSelfMessage` 必须为 `true`（部署脚本与
`rcbot/snowluma.py::ensure_onebot_config` 都会固化它）—— 否则机器人自己发的消息
不会上报，消息页里就只剩别人说的话。

> ★ 容器里不只有 `onebot.json`：QQ 登录后 SnowLuma 会另存一份
> `onebot_<uin>.json` 并**优先使用**，只改前者实测完全不生效。
> `ensure_onebot_config()` 会遍历 `/app/data/config/onebot*.json` 逐份固化，
> 同时把框架自带的 `statusCommand`（也是 `#sl`）关掉 —— 状态指令统一由 rcbot
> 响应，开关在「设置 → 能力 → 允许 #sl 状态指令」，两边都开会对一条 `#sl` 回两条。

> ★ 重启容器后 QQ 可能回到「等待扫码」，需要在「QQ 账户 → 扫码登录」的
> 远程桌面里用手机 QQ 扫一次（登录态文件在卷里，但快登不一定自动完成）。

## 发版三步

```bash
# 1) 改了前端就先构建（会同步 frontend/ 整个目录，含 im/ 子目录）
bash tools/build_frontend.sh QQBot

# 2) 部署（Git Bash 必须带 MSYS_NO_PATHCONV=1，否则 /opt 会被改写成 Windows 路径）
MSYS_NO_PATHCONV=1 python tools/deploy.py plugin --target prod
MSYS_NO_PATHCONV=1 python tools/deploy.py rcbot

# 3) 验收
cd ../../RainCough-Core
node tools/qqbot-probe.mjs http://192.168.2.200:3900 --port 9444 --pw 1
```

## 前端形态约定

照 `plugins/atk` 的做法：**不自带左侧栏、不套外层边框、不写死高度**，
直接铺在面板内容区；导航用顶部 sticky 选项卡；按钮/输入框/开关直接用面板既有类
（`.btn` / `.input` / `.switch`），颜色全走 CSS 变量，浅色深色自动跟随。
