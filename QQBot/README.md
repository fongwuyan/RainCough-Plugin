# QQBot 插件

NapCat（协议端）+ rcbot（机器人本体）的统一控制台。

**接手先读 [`docs/QQ-Bot-接手文档.md`](../../docs/QQ-Bot-接手文档.md)** —— 架构、部署、
配置、接口、排查手册、踩过的坑都在那儿。

## 目录

| 路径 | 说明 |
|---|---|
| `plugin.json` | 插件清单（27 个接口声明），`version` 要和 `VERSION`、`server_v4.py` 三处一致 |
| `server_v4.py` | 插件后端：NapCat WebUI API + rcbot HTTP 的转发层，不持有业务状态 |
| `frontend/plugin.js` | 前端源码（Vue 3），顶部 7 个选项卡 |
| `frontend/qrcode.mjs` | 二维码库（离线内联；NapCat 只给跳转链接，不是图片） |
| `assets/plugin.js` | **构建产物**，面板实际加载这个，改源码后必须重新构建 |
| `rcbot/` `rcbot.py` | 机器人本体源码，部署到 `/opt/rcbot`，由 `rcbot.service` 跑 |
| `tools/deploy.py` | 一键部署（走面板 HTTP，不需要 SSH） |
| `data/config.json` | 插件自己的连接配置（rcbot 地址、NapCat 地址与 token） |

## 发版三步

```bash
# 1) 改了前端就先构建
cp frontend/plugin.js ../../RainCough-Core/plugins/QQBot/frontend/plugin.js
cd ../../RainCough-Core && node tools/build-plugin-frontend.js QQBot
cp plugins/QQBot/assets/plugin.js ../RainCough-Plugin/QQBot/assets/plugin.js
cd ../RainCough-Plugin/QQBot

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
