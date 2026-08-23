# RainCough-Plugin

RainCough 面板可插拔插件集(registry.json 分发)。

## 在面板上安装插件

- 推荐: 面板「插件市场」→ 配置 GitHub Token 后直接从本仓库安装/更新/卸载(仓库为私有, 需 Token; Token 以 AES-256-GCM 存于面板 data/ 配置)。
- 手动: 把插件目录(内含 plugin.py)放入面板 plugins/ 目录并重启面板:
  ```bash
  sudo cp -a backup /opt/touchgal/plugins/          # 示例: 安装 backup 插件
  sudo systemctl restart touchgal.service
  ```
- 已安装插件会出现在 /api/plugins 与侧栏「插件」菜单。

## 插件顶层依赖(建议并入面板 requirements.txt)

部分插件在 import 阶段即依赖以下库, 全新安装面板时若缺失会导致插件加载失败:
- requests : laizhangsetu / uptime
- Pillow   : aigen / laizhangsetu / mcskin
- numpy    : mcskin
- curl_cffi: touchgal / store(面板内置)

## 开发

```bash
python gen_registry.py   # 重新生成 registry.json
```
