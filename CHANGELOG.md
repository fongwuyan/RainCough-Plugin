# 更新日志（插件仓）

规则：**插件版本号只在明确确认后递增**；本仓 `VERSION` 为仓级版本，与面板版本解耦。
每个插件独立维护 `plugin.json:version`，发布时同步本文件的对应分节。

## v1.0.0 — 2026-10-01
- 版本基线统一：17 个插件 `plugin.json:version` 全部为 1.0.0（原 2.0.0/3.0.0 归一）
- `registry.json` 同步重生成：市场清单版本与 `plugin.json` 一致
  （此前清单残留 2.0.0/3.0.0，会让每个已装插件都误报"有更新"）
- JMComic 接口清单补齐 `cover`/`covers`/`prefetch`/`download.cancel`/`perf.stats`
- 仓级 `VERSION` 建立，用于发布与更新比对
- `gen_registry.py` 增加 `--stdout`：不写盘、由调用方落盘（受限环境用）
- 说明：本轮只做版本归一，不改插件功能代码

### 各插件（均 1.0.0）
aigen / compress / dltool / docker / filehash / imagetool / JMComic / kvm /
laizhangsetu / mcserver / mcskin / ocrqr / texttool / touchgal / uptime / vpn / webspy