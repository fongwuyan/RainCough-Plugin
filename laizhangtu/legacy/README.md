# 原始素材存档

本目录保存迁移来源 `E:/jiaob/来张图`（Android QQ 脚本插件，作者「光」，原版本 2.16）
的源码，仅作实现对照与溯源，**面板运行时不会加载这些文件**。

| 文件 | 说明 |
|---|---|
| `main.java` | 原脚本入口：`onMsg` 监听「来张…涩图」、调用 Lolicon API、下载/翻转/模糊图片、发送消息；`showWebDialog` 用 WebView 加载设置页 |
| `utils/ImageUtil.java` | 水平/垂直翻转、RenderScript 高斯模糊、输出 JPEG |
| `settings.html` | 原 WebView 设置页（配置项来源，配色与开关的参考） |
| `info.prop` | 原插件元数据（name / id / version / author / tags） |
| `icon.png` | 原插件图标 |

## 未纳入本插件的内容

- **`缓存/`（约 60MB 本地图片）**：属于个人下载缓存，不是插件资源；其中部分文件名指向不合规内容，因此既不打包也不复制到仓库。面板版改为运行时按需下载到插件自己的 `cache/`，并受 `max_cache_mb` 上限约束。
- **`desc.txt`**：原说明里的标签示例包含涉及未成年人的性化表述，未原样收录；使用方式已在本插件 README 中以中性示例重写。
- **`error.txt`**：调试日志，无参考价值。
- **`images/` 中的大尺寸预览图**：仅保留 `icon.png`。

## 功能映射

| 原脚本（QQ） | 面板插件 v4 |
|---|---|
| Lolicon `/setu/v2` + `tag` 表达式（`&` 与 / `|` 或） | `laizhangtu.fetch`，`parse_tag_expr` 保留同一语法 |
| `size` 原图 / regular / small | `img_size` 0/1/2 |
| 代理 `i.pixiv.re`、排除 AI | `proxy` / `excludeAI` |
| `ImageUtil.flipImage` / `mflipImage` | Pillow `FLIP_LEFT_RIGHT` / `FLIP_TOP_BOTTOM` |
| 「冲多了」随机模糊 | Pillow `GaussianBlur`，概率 `blur_chance` |
| 消息里附标题/作者/pid/uid/尺寸/标签 | 前端作品信息卡（`show_info`） |
| 群冷却、按聊天开关 | 全局 `cool_down`（前端倒计时 + 后端限流） |
| 启动清空缓存 | `max_cache_mb` 超限删最旧 + `laizhangtu.cache.clear` |
| 自动撤回、@提醒、卡片消息、悬浮窗开关 | QQ 消息机制，面板版不适用，已移除 |

另外新增：历史记录（`history.json`）、排除已见（`seen.json`）、配置持久化（`config.json`）、
缓存占用统计，以及输入标签与返回作品的内容安全过滤。
