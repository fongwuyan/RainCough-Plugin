# RainCough-Plugin

RainCough 面板（v6）的插件仓库。插件通过根目录的 `registry.json` 分发。

当前包含 1 个插件：**JMComic**（禁漫天堂搜索与漫画阅读，含配套安卓客户端 JMReader）。

## 安装方式

### 方式一：面板内「插件市场」

1. 打开面板 → 侧栏「插件」→ 顶部「插件市场」页签
2. 若提示上锁，输入插件库口令解锁（30 天内免输）
3. 找到插件 → 点「安装」

面板会从本仓库拉取 `registry.json`，再下载对应目录。公开仓库**不需要 GitHub Token**；
如果面板里还留着失效的旧 Token，程序会自动改用匿名请求（日志会出现
`GitHub token 无效, 改用匿名请求`），不影响使用。

### 方式二：面板内「安装插件」（离线）

侧栏「插件」→ 右上角「安装插件」→ 选择插件包（`.zip` / `.tar.gz` / `.tgz` / `.tar`，上限 128MB）。

包内 `plugin.json` 可以在根目录，也可以在唯一一层子目录下。安装目录取 `plugin.json`
里的 `name`，与压缩包文件名无关。这种方式完全离线，适合没有外网的机器。

### 方式三：手动放置（命令行）

```bash
# 假定面板装在 /home/f/raincough-v6
sudo cp -a JMComic /home/f/raincough-v6/plugins/
sudo systemctl restart rc-v6.service
```

启动后插件会出现在 `/api/plugins` 与侧栏「插件」菜单。首次启动需要在「服务」里
把该插件设为开机自启（autostart），否则面板重启后它不会自动拉起。

## 仓库内含插件

| 插件 | 说明 | 系统依赖 |
|---|---|---|
| `JMComic` | 禁漫天堂搜索与漫画阅读 | Python + `jmcomic` / `requests`（`plugin.json` 的 `requirements` 已声明，面板启动前会预检） |
| `vm` | KVM/QEMU 虚拟机管理：列表、启停、实时监控、创建、快照、VNC 控制台 | `libvirt-clients`(`virsh`) + `qemu-utils`(`qemu-img`)，创建虚拟机额外需要 `virtinst` |

### vm 插件：权限说明

管理虚拟机需要能对 libvirt 的 system 实例做写操作。满足任一条件即可：

1. 面板以 **root** 运行（`install.sh` 默认配置）
2. 运行面板的用户在 **`libvirt` 组**（`sudo usermod -aG libvirt <用户>`，重新登录生效）
3. 该用户具备**免密 sudo**（`NOPASSWD`）
4. libvirt socket 权限开放（如 `0666`）

不满足时插件仍能**列出**虚拟机（libvirt 允许普通用户只读），但启停/创建/删除会被禁用，
界面会明确提示原因，不会静默失败。

安装依赖（Debian/Ubuntu）：

```bash
sudo apt install libvirt-daemon-system libvirt-clients qemu-utils virtinst
sudo systemctl enable --now libvirtd
```

> 插件不保存任何 sudo 密码。早期实现曾把密码写进 `config.json`，现已彻底移除 ——
> 那既会泄露，也会因时间戳过期而失效。

## 插件运行时

v6 面板支持多种语言的插件后端，由 `internal/pluginrt` 自动解析 `backend.exec`：

| 语言 | `backend.lang` | 常见解释器 | 安装（Debian/Ubuntu） |
|---|---|---|---|
| Python | `python` | `python3` | `apt install python3` |
| PHP | `php` | `php` | `apt install php-cli` |
| Java | `java` | `java` / `javac` | `apt install default-jre-headless` |
| Node | `node` | `node` | `apt install nodejs` |
| Go | `go` | 编译好的静态二进制 | 无需运行时 |
| Shell | `bash` | `/bin/sh` | 系统自带 |

`install.sh` 会按 `RC_PLUGIN_LANGS`（默认 `python,php,java,node,go`）自动补齐。
只装 Python 插件的机器可以设 `RC_PLUGIN_LANGS=python` 少装一半东西。

JMComic 需要额外的 Python 包，写在 `JMComic/plugin.json` 的 `requirements` 字段里：

```bash
python3 -m pip install "jmcomic>=2.7" "requests>=2.31"
```

缺包时面板启动插件的日志会明确提示缺哪个模块，不会只留一行 traceback。

## 插件结构（v4 清单）

```
<plugin-name>/
├── plugin.json          # 清单: name/version/frontend/backend/interfaces
├── frontend/plugin.js   # 前端源码(可选, 构建后产出到 assets/)
├── assets/plugin.js     # 构建产物, 面板直接加载这个
└── server_v4.py         # 后端实现(语言不限, 见 backend.exec)
```

`plugin.json` 关键字段：

```jsonc
{
  "name": "JMComic",
  "version": "1.00.1",
  "requirements": ["jmcomic>=2.7", "requests>=2.31"],
  "frontend": { "entry": "plugin.js", "pages": [] },
  "backend": {
    "lang": "python",
    "exec": ["python3", "server_v4.py"],
    "capabilities": ["invoke", "heartbeat", "log.tail"],
    // 声明式 REST 路由: 供移动端 App 等非 RPC 客户端直连
    "rest": [
      { "method": "GET", "path": "/search", "iface": "jmcomic.search",
        "args": { "keyword": "?keyword", "page": "?page" } }
    ],
    "rest_public": true
  },
  "interfaces": [
    { "id": "jmcomic.search", "visibility": "all", "version": "1" }
  ]
}
```

- `backend.exec` 用**解释器名 + 脚本**的形式，面板会做解释器回退
  （`python` → `python3` → `python3.x`），所以老插件写 `python` 也能跑
- `visibility`：`all` 任何人可调；`main` 仅主系统界面可调（通过 REST 桥暴露时，
  桥以 `ui` 身份调用，因此 `main` 接口仍可被 App 访问，前提是清单里声明了对应路由）
- `rest` 是**声明即授权**：没写进 `rest` 的接口不会被任何 HTTP 路由转发

## 前端构建

`frontend/plugin.js` 需要构建成自包含的 `assets/plugin.js`（内联 Vue）：

```bash
# 在面板仓库里执行
node tools/build-plugin-frontend.js JMComic
```

默认用 Vue **生产版**并压缩（619KB → 184KB）。排查问题时可用
`RC_VUE_DEV=1` 切回开发版、`RC_NO_MINIFY=1` 关压缩。

## 维护

```bash
python gen_registry.py            # 扫描所有含 plugin.json 的目录, 重新生成 registry.json
python gen_registry.py --stdout   # 只打印, 不写盘
```

新增插件后必须跑一次，否则面板市场看不到它（`registry.json` 是唯一索引）。

## 相关仓库

- 面板主体：[RainCough-panel-web](https://github.com/fongwuyan/RainCough-panel-web)
- 配套安卓客户端：面板仓库外的 `apk/JMReader`（连接地址填 `http://<面板地址>:3910/JMComic`）
