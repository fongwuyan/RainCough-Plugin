// QQ Bot 插件前端 —— SnowLuma + RainCough Bot 统一控制台
//
// 形态约束（对齐 atk / docker 等插件的做法）：
//  · 不自带左侧栏 —— 宿主已有主导航，插件内导航放顶部横向选项卡
//  · 不套外层边框/固定高度 —— 直接铺在面板内容区里
//  · 颜色、圆角、按钮、输入框全走宿主 CSS 变量与 .btn/.input/.switch 等既有类
//  · ctx.invoke 已解包：成功直接返回 result，失败抛异常 → try/catch
import { createApp, reactive } from 'vue'
// 消息页（仿 QQ 桌面端）：整屏 overlay，独立样式与数据层
import { IM } from './im/shell.js'
import { injectIMStyle } from './im/tokens.js'
import { setCtx as setIMCtx } from './im/store.js'

const NAME = 'qqbot'
const STYLE_ID = 'rcq-style'
const LS_TAB = 'rcq.tab'

let CTX = null

const S = reactive({ toast: '', toastKind: '', conn: null })

let toastTimer = null
function toast(msg, kind) {
  S.toast = String(msg == null ? '' : msg)
  S.toastKind = kind || ''
  if (toastTimer) clearTimeout(toastTimer)
  toastTimer = setTimeout(() => { S.toast = '' }, kind === 'err' ? 5200 : 2600)
}

async function call(iface, params, opts) {
  if (!CTX || !CTX.invoke) throw new Error('插件运行时未就绪')
  return await CTX.invoke(iface, params || {}, opts)
}

// rcbot.* 接口统一返回 {ok, data}，这里解包成 data；没有 data 字段就原样返回
async function callData(iface, params, opts) {
  const r = await call(iface, params, opts)
  return (r && typeof r === 'object' && 'data' in r && r.data !== null && r.data !== undefined)
    ? r.data : r
}

function errText(e) {
  if (!e) return '未知错误'
  return String((e && e.message) || e)
}

const p2 = (n) => (n < 10 ? '0' + n : '' + n)
function fmtTime(ts) {
  if (!ts) return '—'
  const d = new Date(ts * 1000)
  return (d.getMonth() + 1) + '-' + p2(d.getDate()) + ' ' + p2(d.getHours()) + ':' + p2(d.getMinutes())
}
function fmtFull(ts) {
  if (!ts) return '—'
  const d = new Date(ts * 1000)
  return d.getFullYear() + '-' + p2(d.getMonth() + 1) + '-' + p2(d.getDate()) + ' ' +
    p2(d.getHours()) + ':' + p2(d.getMinutes()) + ':' + p2(d.getSeconds())
}
function fmtNum(n) {
  if (n == null || n === '') return '—'
  n = Number(n)
  if (isNaN(n)) return '—'
  if (n >= 1e6) return (n / 1e6).toFixed(1) + 'M'
  if (n >= 1e4) return (n / 1e4).toFixed(1) + '万'
  return String(n)
}
function splitList(s) {
  return String(s || '').split(/[,，\s]+/).map((x) => x.trim()).filter(Boolean)
}
// 媒体文件 URL：走面板的文件预览通道（能读任意路径，且 http.ServeFile 支持 Range）
//
// ★ 优先用后端给的绝对路径（m.abs）：媒体根目录是配置项（config.chat.media_dir），
//   在前端硬编码 /opt/rcbot/media 的话，改了配置就全找不到文件了。
function mediaFileUrl(m) {
  if (!m) return ''
  const p = m.abs || (m.rel ? '/opt/rcbot/media/' + m.rel : '')
  if (!p) return ''
  return '/api/fm/preview?path=' + encodeURIComponent(p)
}

// 媒体文件在本机是否还可用（被删/被清过就是 false）。
// false 就不该再去发请求 —— 发了就是一片 404。
function mediaAlive(md) {
  if (!md || !md.local) return false
  return md.exists !== 0
}

// ------------------------------------------------------------------ 缩略图
// 媒体库/查询一次要显示几十张图，直接 <img src=原图> 会一屏拉 10MB+。
// 这里只在滚到可视区时才请后端生成 320px 缩略图（磁盘缓存），点开再看原图。
const _thumbCache = new Map()
const THUMB_BLANK = 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'
const ThumbImg = {
  name: 'ThumbImg',
  props: { rel: String, size: { type: Number, default: 360 } },
  data() { return { src: '', io: null } },
  computed: { blank() { return THUMB_BLANK } },
  mounted() {
    const key = this.rel + '@' + this.size
    const hit = _thumbCache.get(key)
    if (hit) { this.src = hit; return }
    if (typeof IntersectionObserver === 'undefined') { this.load(); return }
    this.io = new IntersectionObserver((es) => {
      if (es.some((e) => e.isIntersecting)) {
        this.io.disconnect(); this.io = null; this.load()
      }
    }, { rootMargin: '240px' })
    this.io.observe(this.$el)
  },
  beforeUnmount() { if (this.io) this.io.disconnect() },
  methods: {
    async load() {
      const key = this.rel + '@' + this.size
      const hit = _thumbCache.get(key)
      if (hit) { this.src = hit; return }
      try {
        const d = await callData('qqbot.chat.thumb', { rel: this.rel, size: this.size })
        if (d && d.path) {
          const u = '/api/fm/preview?path=' + encodeURIComponent(d.path)
          _thumbCache.set(key, u)
          this.src = u
        }
      } catch (e) { /* 缩略图失败就留空，不影响原图查看 */ }
    },
  },
  // 占位透明图：必须始终是可渲染元素，display:none 的元素不会被 IntersectionObserver 命中
  template: `<img :src="src || blank" decoding="async" alt="" />`,
}

// ------------------------------------------------------------------ 样式

const CSS = `
.rcq{--t:var(--text);--m:var(--text-muted);--f:var(--text-faint);--bd:var(--border);
 --bd2:var(--border-strong);--sf:var(--surface);--sf2:var(--surface-2);--sf3:var(--surface-3);
 --ac:var(--accent);--acbg:var(--accent-soft);--ok:var(--success);--warn:var(--warning);
 --bad:var(--danger);--r:var(--radius-md);
 color:var(--t);font-size:13px;line-height:1.6;font-family:var(--font)}
.rcq *{box-sizing:border-box}

/* 顶部选项卡（插件内唯一导航）：胶囊式，活动项用主题色底 */
.rcq-bar{position:sticky;top:0;z-index:9;display:flex;align-items:center;gap:4px;flex-wrap:wrap;
 padding:5px 6px;background:var(--sf2);border:1px solid var(--bd);border-radius:12px;
 margin-bottom:14px;backdrop-filter:blur(8px)}
.rcq-tab{padding:6px 12px;font-size:13px;color:var(--m);cursor:pointer;user-select:none;
 border-radius:8px;white-space:nowrap;transition:background .12s,color .12s}
.rcq-tab:hover{color:var(--t);background:var(--sf3)}
.rcq-tab.on{color:var(--ac);background:var(--acbg);font-weight:600}
.rcq-bar-r{margin-left:auto;display:flex;align-items:center;gap:10px;padding:0 4px}
.rcq-lamp{display:inline-flex;align-items:center;gap:5px;font-size:11px;color:var(--m)}
.rcq-lamp b{width:7px;height:7px;border-radius:50%;background:var(--bd2);display:inline-block}
.rcq-lamp b.on{background:var(--ok);box-shadow:0 0 0 3px rgba(63,185,80,.16)}
.rcq-lamp b.off{background:var(--bad)}

/* 卡片 */
.rcq-pnl{background:var(--sf);border:1px solid var(--bd);border-radius:var(--r);
 padding:15px 17px;margin-bottom:12px}
.rcq-pnl.flat{padding:0}
.rcq-ph{display:flex;align-items:center;gap:8px;margin-bottom:12px;min-height:24px;flex-wrap:wrap}
.rcq-ph b{font-size:14px;font-weight:600;letter-spacing:.2px}
.rcq-ph .sp{margin-left:auto}
.rcq-sec{border-top:1px solid var(--bd);margin:12px -16px;padding:12px 16px 0}
/* .rcq-pnl.flat 自身 padding 为 0，负边距会把内容顶到边框上（概览的「系统信息」就是），
   这种卡片里的分隔段改成正常内边距，分隔线仍然横贯整张卡 */
.rcq-pnl.flat > .rcq-sec{margin-left:0;margin-right:0;padding:12px 16px 0}

/* 键值 */
.rcq-kv{display:grid;grid-template-columns:88px 1fr;gap:7px 12px;font-size:12.5px;align-items:baseline}
.rcq-kv .k{color:var(--m)}
.rcq-kv .v{color:var(--t);font-family:var(--font-mono);word-break:break-all}
.rcq-fld{display:flex;align-items:baseline;gap:7px;font-size:12.5px;min-width:0}
.rcq-fld .k{color:var(--m);flex:none}
.rcq-fld .v{color:var(--t);font-family:var(--font-mono);word-break:break-all}
.rcq-fld.full{grid-column:1/-1}
.rcq-row2{display:grid;grid-template-columns:1fr 1fr;gap:9px 16px;margin-top:9px}
.rcq-row2 > .full{grid-column:1/-1}

/* 概览三栏 */
.rcq-ov{display:grid;grid-template-columns:minmax(230px,.95fr) minmax(0,1.5fr) 160px;
 gap:12px;align-items:start}
.rcq-ov > div > .rcq-pnl:last-child{margin-bottom:0}
.rcq-acct{display:flex;align-items:center;gap:12px;padding:16px}
.rcq-ava{width:52px;height:52px;border-radius:50%;object-fit:cover;flex:none;
 background:var(--sf2);border:1px solid var(--bd)}
.rcq-nick{font-size:14px;font-weight:600;display:flex;align-items:center;gap:7px}
.rcq-dot{width:7px;height:7px;border-radius:50%;background:var(--bd2);display:inline-block;flex:none}
.rcq-dot.on{background:var(--ok)}
.rcq-dot.off{background:var(--bad)}
.rcq-uin{font-size:11.5px;color:var(--m);font-family:var(--font-mono);margin-top:2px}

/* 仪表 */
.rcq-gauges{display:flex;flex-direction:column;gap:12px}
.rcq-gauge{position:relative;display:flex;align-items:center;justify-content:center;
 padding:12px 6px;background:var(--sf);border:1px solid var(--bd);border-radius:var(--r)}
.rcq-gauge svg{width:96px;height:96px;display:block}
.rcq-gauge .lbl{position:absolute;inset:0;display:flex;flex-direction:column;
 align-items:center;justify-content:center;pointer-events:none}
.rcq-gauge .lbl b{font-size:17px;font-weight:700;line-height:1.1}
.rcq-gauge .lbl span{font-size:10px;color:var(--m);margin-top:1px}

/* 计数条 */
.rcq-counters{display:grid;grid-template-columns:repeat(5,1fr);background:var(--sf);
 border:1px solid var(--bd);border-radius:var(--r);overflow:hidden;margin-bottom:12px}
.rcq-ct{padding:13px 6px;text-align:center;border-left:1px solid var(--bd)}
.rcq-ct:first-child{border-left:0}
.rcq-ct b{display:block;font-size:23px;font-weight:700;line-height:1.2}
.rcq-ct span{font-size:11px;color:var(--m)}

/* 列表 */
.rcq-list{display:flex;flex-direction:column}
.rcq-row{display:flex;align-items:center;gap:10px;padding:10px 16px;border-top:1px solid var(--bd);
 cursor:default}
.rcq-row:first-child{border-top:0}
.rcq-row.click{cursor:pointer}
.rcq-row.click:hover,.rcq-row.on{background:var(--sf2)}
.rcq-row .main{flex:1;min-width:0}
.rcq-row .t{font-size:12.5px;font-weight:600;display:flex;align-items:center;gap:6px;flex-wrap:wrap}
.rcq-row .d{font-size:11.5px;color:var(--m);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;margin-top:1px}
.rcq-row .acts{display:flex;gap:6px;flex:none;align-items:center}
/* 会话列表行内的启用开关：垂直居中、不撑高行高 */
.rcq-row .acts .switch{margin:0;display:inline-flex;align-items:center}
.rcq-row .acts .switch input{width:30px;height:17px}
.rcq-mono{font-family:var(--font-mono);font-size:11.5px}

.rcq-empty{padding:38px 12px;text-align:center;color:var(--f);font-size:12.5px}
.rcq-empty b{display:block;font-size:24px;margin-bottom:6px;opacity:.45;font-weight:400}

/* 二维码 */
.rcq-qr{width:196px;height:196px;background:#fff;border:1px solid var(--bd);
 border-radius:var(--r);padding:9px;display:flex;align-items:center;justify-content:center;flex:none}
.rcq-qr svg{width:100%;height:100%;display:block}
.rcq-qr .ph{color:#999;font-size:12px;text-align:center;padding:0 10px}

/* 日志（SnowLuma 容器日志：纯文本行，按级别着色） */
.rcq-log{background:var(--sf);border:1px solid var(--bd);border-radius:var(--r);
 padding:11px 13px;font-family:var(--font-mono);font-size:11.5px;line-height:1.85;
 max-height:min(64vh,640px);overflow:auto;white-space:pre-wrap;word-break:break-word}
/* 级别类名一律加 rcq-lv- 前缀：面板全局有 .error{padding:24px;text-align:center}，
   直接写 class="error" 会把日志行搞成居中的大块 */
.rcq-ln{color:var(--t);padding:0;text-align:left}
.rcq-ln .lv{font-weight:700;margin-right:5px}
.rcq-ln.rcq-lv-info .lv{color:var(--m)}
.rcq-ln.rcq-lv-debug{color:var(--f)}
.rcq-ln.rcq-lv-debug .lv{color:var(--f)}
.rcq-ln.rcq-lv-warn{color:var(--warn)}
.rcq-ln.rcq-lv-error{color:var(--bad)}
.rcq-ln.rcq-lv-fatal{color:var(--bad);font-weight:600}
.rcq-pill{display:inline-flex;align-items:center;gap:5px;padding:2px 9px;font-size:11px;
 border:1px solid var(--bd2);border-radius:999px;color:var(--m);white-space:nowrap}
.rcq-pill.ok{color:var(--ok);border-color:var(--ok)}
.rcq-pill.off{color:var(--bad);border-color:var(--bad)}
.rcq-qr-ok{display:flex;flex-direction:column;align-items:center;justify-content:center;
 gap:6px;color:var(--ok);font-size:12.5px;text-align:center;width:100%;height:100%}
.rcq-qr-ok b{font-size:30px;font-weight:400;line-height:1}

/* 表单 */
.rcq-form{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px}
.rcq-fi{display:flex;flex-direction:column;gap:5px;min-width:0}
.rcq-fi > span{font-size:11.5px;color:var(--m)}
.rcq-fi.wide{grid-column:1/-1}
.rcq-fi > .switch{align-self:flex-start;margin-top:3px}
.rcq-fi > .rcq-num{max-width:220px}
.rcq-ta{width:100%;min-height:132px;resize:vertical;padding:9px 11px;font-size:12.5px;
 line-height:1.7;font-family:var(--font-mono);color:var(--t);background:var(--surface);
 border:1px solid var(--bd);border-radius:var(--r)}
.rcq-ta:focus{outline:none;border-color:var(--ac);box-shadow:var(--ring)}
.rcq-note{font-size:11px;color:var(--f);margin-top:4px;line-height:1.55}
/* 报错原文可能很长（模型返回的 JSON），两行截断，悬停看全文 */
.rcq-err{color:var(--bad);white-space:normal;word-break:break-word;
 display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}

/* 会话详情 */
.rcq-msgs{max-height:min(46vh,460px);overflow:auto;padding:2px 0}
.rcq-msg{display:flex;gap:9px;padding:7px 0;border-top:1px dashed var(--bd)}
.rcq-msg:first-child{border-top:0}
.rcq-msg .who{flex:none;width:74px;font-size:11px;color:var(--m);text-align:right;
 overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.rcq-msg .body{flex:1;min-width:0;font-size:12.5px;white-space:pre-wrap;word-break:break-word}
.rcq-msg.me .who{color:var(--ac)}
.rcq-bar2{height:6px;background:var(--sf3);border-radius:3px;overflow:hidden;margin-top:6px}
.rcq-bar2 i{display:block;height:100%;background:var(--ac);border-radius:3px}
.rcq-bar2 i.hi{background:var(--warn)}
.rcq-bar2 i.max{background:var(--bad)}

.rcq-split{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.25fr);gap:12px;align-items:start}
.rcq-flex{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.rcq-hint{font-size:11.5px;color:var(--m)}
.rcq-warn{border-color:var(--warn);color:var(--warn)}

/* ---- 多实例（QQ 账户） ---- */
.rcq-inst{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:12px}
.rcq-icard{background:var(--sf);border:1px solid var(--bd);border-radius:var(--r);padding:14px 15px}
.rcq-icard.on{border-color:var(--ac)}
.rcq-itop{display:flex;align-items:center;gap:10px;margin-bottom:10px}
.rcq-itop .nm{flex:1;min-width:0}
.rcq-itop .nm b{display:block;font-size:13.5px;font-weight:600;overflow:hidden;
 text-overflow:ellipsis;white-space:nowrap}
.rcq-itop .nm span{font-size:11.5px;color:var(--m);font-family:var(--font-mono)}
.rcq-imeta{display:grid;grid-template-columns:auto 1fr;gap:4px 10px;font-size:11.5px;
 margin-bottom:10px}
.rcq-imeta .k{color:var(--m)}
.rcq-imeta .v{font-family:var(--font-mono);word-break:break-all}
.rcq-iacts{display:flex;gap:6px;flex-wrap:wrap;align-items:center}


/* ---- 媒体库 ---- */
.rcq-mlib{display:grid;grid-template-columns:repeat(auto-fill,minmax(168px,1fr));gap:10px}
.rcq-mcard{background:var(--sf);border:1px solid var(--bd);border-radius:var(--r);
 overflow:hidden;display:flex;flex-direction:column;position:relative}
.rcq-mcard.on{border-color:var(--ac);box-shadow:0 0 0 1px var(--ac)}
.rcq-mcard.gone{opacity:.55}
.rcq-mcard .ck{position:absolute;top:6px;left:6px;z-index:2;background:rgba(0,0,0,.45);
 border-radius:5px;padding:1px 5px;line-height:1.4}
.rcq-mcard .th{height:118px;background:var(--sf3);display:flex;align-items:center;
 justify-content:center;overflow:hidden;cursor:zoom-in;position:relative}
.rcq-mcard .th img{width:100%;height:100%;object-fit:cover;display:block}
.rcq-mcard .th video{width:100%;height:100%;object-fit:cover;display:block}
.rcq-mcard .th .ph{font-size:30px;opacity:.6}
.rcq-mcard .meta{padding:7px 9px;font-size:11px;color:var(--m);flex:1;min-width:0}
.rcq-mcard .meta .n{font-size:11.5px;color:var(--t);font-weight:600}
.rcq-mcard .meta .s,.rcq-mcard .meta .t{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.rcq-mcard .dl{display:block;text-align:center;padding:5px;border-top:1px solid var(--bd);
 font-size:11px;color:var(--ac);text-decoration:none}
.rcq-mcard .dl:hover{background:var(--sf2)}
.rcq-mcard .dl.gone{color:var(--m);cursor:default}

/* 骨架屏（首屏加载中占位，避免"白屏 + 突然出现"） */
.rcq-mcard.skel{pointer-events:none}
.rcq-mcard.skel .th{background:var(--sf2);animation:rcq-pulse 1.2s ease-in-out infinite}
.rcq-mcard.skel .meta .n,.rcq-mcard.skel .meta .s{height:9px;background:var(--sf2);border-radius:4px;margin:4px 0}
.rcq-qrow.skel{pointer-events:none}
.rcq-qrow.skel .ava-sk{width:18px;height:18px;border-radius:50%;background:var(--sf2);display:inline-block}
.rcq-qrow.skel .ln-sk{display:block;height:9px;background:var(--sf2);border-radius:4px;margin:5px 0}
.rcq-qrow.skel .w40{width:40%}.rcq-qrow.skel .w80{width:80%}.rcq-qrow.skel .w60{width:60%}
@keyframes rcq-pulse{0%,100%{opacity:.5}50%{opacity:.95}}

/* 媒体库筛选网格 / 更多菜单 / 批量条 */
.rcq-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px 14px;align-items:end}
.rcq-grid .rcq-fi{margin:0}
.rcq-grid .rcq-hit{align-self:center}
.rcq-acts{display:flex;gap:8px;justify-content:flex-end;align-items:end}
.rcq-more{position:relative}
.rcq-more-pop{position:absolute;right:0;top:calc(100% + 6px);z-index:8;background:var(--sf);border:1px solid var(--bd);
 border-radius:10px;box-shadow:0 8px 24px rgba(0,0,0,.22);padding:4px;min-width:160px;display:flex;flex-direction:column}
.rcq-more-pop button{border:none;background:none;text-align:left;padding:7px 10px;border-radius:6px;
 color:var(--t);font-family:inherit;font-size:12px;cursor:pointer}
.rcq-more-pop button:hover{background:var(--sf2)}
.rcq-more-pop button:disabled{opacity:.45;cursor:default}
.rcq-batch{position:sticky;bottom:12px;z-index:7;margin:12px 0 0;display:flex;align-items:center;gap:10px;flex-wrap:wrap;
 background:var(--sf);border:1px solid var(--bd);border-radius:12px;padding:10px 14px;box-shadow:0 8px 24px rgba(0,0,0,.25)}
.rcq-mcard .vid-ic{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;
 font-size:26px;color:#fff;text-shadow:0 2px 10px rgba(0,0,0,.65);pointer-events:none}
.rcq-badge{display:inline-block;font-size:10px;line-height:1.7;padding:0 6px;border-radius:999px;
 border:1px solid var(--bd);color:var(--m);margin-left:4px;vertical-align:middle}
.rcq-badge.warn{border-color:var(--warn);color:var(--warn)}
.rcq-badge.bad{border-color:var(--bad);color:var(--bad)}
.rcq-badge.plain{border-style:dashed}

/* ---- 查询 ---- */
.rcq-qres{display:flex;flex-direction:column;gap:6px}
.rcq-qrow{background:var(--sf);border:1px solid var(--bd);border-radius:var(--r);padding:8px 11px}
.rcq-qrow.rec{opacity:.72}
.rcq-qrow .hd{display:flex;align-items:center;gap:6px;flex-wrap:wrap;font-size:11.5px;color:var(--m)}
.rcq-qrow .hd .ava{width:18px;height:18px;border-radius:50%;object-fit:cover;flex:none}
.rcq-qrow .hd b{font-size:12px;color:var(--t)}
.rcq-qrow .hd .tt{margin-left:auto}
.rcq-qrow .bd{margin-top:5px;font-size:12.5px;white-space:pre-wrap;word-break:break-word;line-height:1.55}
.rcq-sugg{position:absolute;top:100%;left:0;right:0;z-index:50;background:var(--sf);
 border:1px solid var(--bd);border-radius:var(--r);box-shadow:var(--shadow);margin-top:2px;
 max-height:230px;overflow:auto}
.rcq-sugg-i{display:flex;align-items:center;gap:7px;padding:6px 9px;cursor:pointer;font-size:12px}
.rcq-sugg-i:hover{background:var(--sf2)}
.rcq-sugg-i img{width:20px;height:20px;border-radius:50%;object-fit:cover}
.rcq-sugg-i b{font-weight:600}
.rcq-sugg-i span{color:var(--m);font-size:11px}
.rcq-sugg-i i{margin-left:auto;font-style:normal;color:var(--m);font-size:11px}
.rcq-noplay{display:inline-flex;align-items:center;gap:6px;font-size:11.5px;color:var(--warn);
 border:1px solid var(--warn);border-radius:7px;padding:4px 9px;margin-top:5px}
.rcq-noplay a{color:var(--ac)}

/* 大图查看 */
.rcq-light{position:fixed;inset:0;z-index:9998;background:rgba(0,0,0,.82);
 display:flex;align-items:center;justify-content:center;padding:24px;cursor:zoom-out}
.rcq-light img{max-width:100%;max-height:100%;border-radius:8px}
.rcq-light .x{position:absolute;top:16px;right:20px;color:#fff;font-size:24px;
 background:none;border:none;cursor:pointer;line-height:1}

/* 水位条 */
.rcq-wl{height:6px;background:var(--sf3);border-radius:3px;overflow:hidden;margin-top:6px}
.rcq-wl i{display:block;height:100%;background:var(--ok);border-radius:3px}
.rcq-wl i.hi{background:var(--warn)}
.rcq-wl i.max{background:var(--bad)}

/* toast */
.rcq-toast{position:fixed;right:24px;bottom:24px;z-index:9999;max-width:420px;
 padding:10px 15px;font-size:12.5px;background:var(--surface-3);color:var(--text);
 border:1px solid var(--border-strong);border-radius:var(--radius-md);box-shadow:var(--shadow)}
.rcq-toast.ok{border-color:var(--success);color:var(--success)}
.rcq-toast.err{border-color:var(--danger);color:var(--danger)}

@media(max-width:1180px){
 .rcq-ov{grid-template-columns:minmax(0,1fr) minmax(0,1.2fr)}
 .rcq-gauges{grid-column:1/-1;flex-direction:row;justify-content:center;gap:12px}
 .rcq-gauge{flex:1;max-width:240px}
}
@media(max-width:820px){
 .rcq-ov{grid-template-columns:1fr}
 .rcq-split{grid-template-columns:1fr}
 .rcq-counters{grid-template-columns:repeat(3,1fr)}
 .rcq-ct:nth-child(4){border-left:0;border-top:1px solid var(--bd)}
 .rcq-ct:nth-child(5){border-top:1px solid var(--bd)}
}

/* ---- 角色卡片 ---- */
/* 列表：卡片墙 */
.cd-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:10px;padding:12px}
.cd-card{position:relative;border:1px solid var(--bd);border-radius:12px;overflow:hidden;
  background:var(--sf);cursor:pointer;transition:transform .12s ease,box-shadow .12s ease}
.cd-card:hover{transform:translateY(-2px);box-shadow:var(--shadow)}
.cd-card.on{border-color:var(--ac);box-shadow:0 0 0 1px var(--ac)}
.cdc-cover{position:relative;aspect-ratio:16/10;background:linear-gradient(135deg,var(--sf3),var(--sf2));
  background-size:cover;background-position:center;display:flex;align-items:center;justify-content:center}
.cdc-fallback{font-size:30px;font-weight:600;color:rgba(255,255,255,.92);
  text-shadow:0 2px 8px rgba(0,0,0,.28)}
.cdc-ava{position:absolute;left:10px;bottom:-14px;width:38px;height:38px;border-radius:10px;
  object-fit:cover;border:2px solid var(--sf);background:var(--sf3)}
.cdc-body{padding:18px 10px 10px}
.cdc-name{font-size:13px;font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.cdc-tag{font-size:11px;color:var(--m);margin-top:2px;line-height:1.35;
  display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;min-height:2.7em}
.cdc-badges{margin-top:6px;display:flex;gap:4px;flex-wrap:wrap}
.cd-tag.v{color:var(--f)}

/* 详情：一张完整的大卡片 */
.cd-hero{position:relative;border:1px solid var(--bd);border-radius:14px;overflow:hidden;
  background:var(--sf);margin:10px 0 14px}
.cdh-cover{position:absolute;left:0;right:0;top:0;height:132px;background-size:cover;
  background-position:center 28%;opacity:.85}
.cdh-cover::after{content:"";position:absolute;inset:0;
  background:linear-gradient(180deg,rgba(0,0,0,0) 40%,rgba(0,0,0,.30) 100%)}
.cdh-inner{position:relative;display:flex;align-items:center;gap:13px;padding:18px 18px 14px}
.cd-hero.grad .cdh-name{color:#fff;text-shadow:0 1px 6px rgba(0,0,0,.35)}
.cd-hero.grad .cdh-alias{color:rgba(255,255,255,.82)}
.cd-hero.grad .cdh-tag{color:rgba(255,255,255,.92)}
.cd-hero.grad .cdh-ava{background:rgba(255,255,255,.22);color:#fff;
  border:1px solid rgba(255,255,255,.45)}
.cd-hero.grad .cd-tag{color:#fff;border-color:rgba(255,255,255,.55)}
.cd-hero.grad .cdh-inner::before{content:"";position:absolute;inset:0;
  background:linear-gradient(180deg,rgba(0,0,0,.30),rgba(0,0,0,.05));pointer-events:none}
.cdh-ava{width:58px;height:58px;border-radius:15px;overflow:hidden;background:var(--sf3);
  display:flex;align-items:center;justify-content:center;font-size:23px;font-weight:600;color:var(--f);
  box-shadow:0 4px 14px rgba(0,0,0,.20);flex:none}
.cdh-ava img{width:100%;height:100%;object-fit:cover;display:block}
.cdh-title{flex:1;min-width:0}
.cdh-name{font-size:17px;font-weight:700;letter-spacing:.01em}
.cdh-alias{font-size:11.5px;color:var(--m);margin-top:2px}
.cdh-tag{font-size:12.5px;color:var(--m);margin-top:4px}
.cdh-badges{display:flex;gap:6px;margin-top:7px;flex-wrap:wrap}
.cdh-sections{position:relative;background:var(--sf);border-top:1px solid var(--bd);
  padding:12px 18px 16px;
  display:grid;gap:14px;grid-template-columns:repeat(auto-fit,minmax(230px,1fr))}
.cdh-sec{font-size:12.5px;line-height:1.6;min-width:0}
.cdh-sec>b{display:block;font-size:10.5px;color:var(--f);margin-bottom:5px;letter-spacing:.06em}
.cdh-line{margin-bottom:3px}
.cdh-ex{margin-bottom:7px}
.cdh-ex .u{font-size:11.5px;color:var(--m)}
.cdh-ex .a{margin-top:1px}
.cdh-lore{font-size:11.5px;color:var(--m);margin-bottom:6px;line-height:1.5}
.cdh-lore .k{display:inline-block;margin-right:5px;color:var(--ac)}

.cd-tabs{display:flex;gap:4px;margin:10px 0 0;border-bottom:1px solid var(--bd)}
.cd-tabs button{border:none;background:none;padding:7px 12px;font-size:12.5px;color:var(--m);
  cursor:pointer;border-bottom:2px solid transparent;font-family:inherit}
.cd-tabs button.on{border-bottom-color:var(--ac);font-weight:600}
.cd-blk{border:1px solid var(--bd);border-radius:8px;padding:9px 11px;margin-top:10px}
.cd-blk-h{display:flex;align-items:center;gap:8px;margin-bottom:6px;font-size:12.5px}
.cd-blk-h .sp{flex:1}
.cd-item{display:flex;gap:6px;align-items:flex-start;margin-bottom:6px}
.cd-item.col{flex-direction:column}
.cd-item .rcq-ta{flex:1;min-height:52px}
.cd-row2{display:flex;gap:6px;align-items:center;width:100%}
.cd-row2 .input{flex:1;min-width:0}
.cd-x{border:none;background:none;color:var(--m);font-size:15px;line-height:1;cursor:pointer;
  padding:2px 5px;border-radius:4px;font-family:inherit}
.cd-x:hover{background:var(--sf3)}
.rcq-ta.tall{min-height:140px}
`

function injectStyle() {
  if (document.getElementById(STYLE_ID)) return
  const el = document.createElement('style')
  el.id = STYLE_ID
  el.textContent = CSS
  document.head.appendChild(el)
}


// ------------------------------------------------------------------ 概览（SnowLuma）

const Overview = {
  data() { return { S, ov: null, busy: false, err: '', timer: null } },
  computed: {
    acc() { return (this.ov && this.ov.account) || {} },
    ver() { return (this.ov && this.ov.versions) || {} },
    sysinfo() { return (this.ov && this.ov.sys) || {} },
    cpu() { return this.sysinfo.cpu || {} },
    mem() { return this.sysinfo.memory || {} },
    cnt() { return (this.ov && this.ov.counters) || {} },
    botst() { return (this.ov && this.ov.bot) || null },
    // 单后端：版本区三行固定是框架 / QQ / OneBot 网关
    vers() {
      const v = this.ver
      return [['框架版本', v.framework], ['QQ 版本', v.qq], ['OneBot 版本', v.webui]]
    },
    cpuPct() {
      const v = parseFloat((this.cpu.usage || {}).system)
      return isNaN(v) ? 0 : Math.min(100, Math.round(v))
    },
    memPct() {
      const t = parseFloat(this.mem.total)
      const u = parseFloat((this.mem.usage || {}).system)
      if (!t || !u) return 0
      return Math.min(100, Math.round((u / t) * 100))
    },
    online() { return !!this.acc.login && !this.acc.offline },
  },
  async mounted() {
    // ★ 这里以前有一句 this.loadBackend()，但那是「QQ 账户」页的方法，
    //   概览页没有 → mounted 直接抛 TypeError，ov 永远不加载，
    //   整页停在"未登录/—"，而且 5 秒轮询也没起来（看着像后端挂了）。
    //   概览的框架信息来自 overview 自己的 backend 字段，不需要单独拉。
    await this.load()
    this.timer = setInterval(() => this.load(true), 5000)
  },
  beforeUnmount() { if (this.timer) clearInterval(this.timer) },
  methods: {
    fmtNum,
    async load(silent) {
      if (!silent) this.busy = true
      try {
        this.ov = await call('qqbot.overview')
        this.err = (this.ov.errors || []).join('；')
      } catch (e) {
        this.err = errText(e)
      } finally {
        this.busy = false
      }
    },
    dash(pct) { return 264 - (264 * pct) / 100 },
    // 头像：后端已按 QQ 号兜底拼好，这里再兜一层（后端没给但有号时）
    accAvatar(a) {
      if (a.avatar) return a.avatar
      const uin = String((a && a.uin) || '')
      if (!/^\d{5,12}$/.test(uin)) return ''
      return 'https://q1.qlogo.cn/g?b=qq&nk=' + uin + '&s=100'
    },
  },
  template: `
  <div>
    <div v-if="err" class="rcq-pnl rcq-warn" style="font-size:12px">{{ err }}</div>

    <div class="rcq-ov">
      <div>
        <div class="rcq-pnl flat">
          <div class="rcq-acct">
            <img class="rcq-ava" :src="accAvatar(acc)" alt="" v-if="accAvatar(acc)" />
            <div class="rcq-ava" v-else></div>
            <div style="min-width:0">
              <div class="rcq-nick">
                {{ acc.nick || '未登录' }}
                <span class="rcq-dot" :class="online ? 'on' : 'off'"></span>
              </div>
              <div class="rcq-uin">{{ acc.uin || '—' }}</div>
            </div>
          </div>
          <div class="rcq-sec">
            <div class="rcq-ph" style="margin-bottom:10px"><b>系统信息</b></div>
            <div class="rcq-kv">
              <template v-for="row in vers" :key="row[0]">
                <div class="k">{{ row[0] }}</div><div class="v">{{ row[1] || '—' }}</div>
              </template>
              <div class="k">系统版本</div><div class="v">{{ sysinfo.arch || '—' }}</div>
            </div>
          </div>
        </div>
      </div>

      <div>
        <div class="rcq-pnl">
          <div class="rcq-ph"><b>CPU</b><span class="sp"></span>
            <span class="rcq-hint">{{ busy ? '刷新中…' : '' }}</span></div>
          <div class="rcq-fld full"><span class="k">型号</span><span class="v">{{ cpu.model || '—' }}</span></div>
          <div class="rcq-row2">
            <div class="rcq-fld"><span class="k">内核数</span><span class="v">{{ cpu.core || '—' }}</span></div>
            <div class="rcq-fld"><span class="k">主频</span><span class="v">{{ cpu.speed ? cpu.speed + ' GHz' : '—' }}</span></div>
            <div class="rcq-fld"><span class="k">使用率</span><span class="v">{{ (cpu.usage||{}).system || '—' }}%</span></div>
            <div class="rcq-fld"><span class="k">QQ主线程</span><span class="v">{{ (cpu.usage||{}).qq || '—' }}%</span></div>
          </div>
          <div class="rcq-sec">
            <div class="rcq-ph" style="margin-bottom:10px"><b>内存</b></div>
            <div class="rcq-fld full"><span class="k">总量</span><span class="v">{{ mem.total ? mem.total + ' MB' : '—' }}</span></div>
            <div class="rcq-row2">
              <div class="rcq-fld"><span class="k">使用量</span><span class="v">{{ (mem.usage||{}).system ? (mem.usage||{}).system + ' MB' : '—' }}</span></div>
              <div class="rcq-fld"><span class="k">QQ主线程</span><span class="v">{{ (mem.usage||{}).qq ? (mem.usage||{}).qq + ' MB' : '—' }}</span></div>
            </div>
          </div>
        </div>
      </div>

      <div class="rcq-gauges">
        <div class="rcq-gauge">
          <svg viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="42" fill="none" stroke="var(--sf3)" stroke-width="9" />
            <circle cx="50" cy="50" r="42" fill="none" stroke="var(--ac)" stroke-width="9"
              stroke-linecap="round" :stroke-dasharray="264" :stroke-dashoffset="dash(cpuPct)"
              transform="rotate(-90 50 50)" />
          </svg>
          <div class="lbl"><b>{{ cpuPct }}%</b><span>CPU 占用</span></div>
        </div>
        <div class="rcq-gauge">
          <svg viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="42" fill="none" stroke="var(--sf3)" stroke-width="9" />
            <circle cx="50" cy="50" r="42" fill="none" stroke="var(--ac)" stroke-width="9"
              stroke-linecap="round" :stroke-dasharray="264" :stroke-dashoffset="dash(memPct)"
              transform="rotate(-90 50 50)" />
          </svg>
          <div class="lbl"><b>{{ memPct }}%</b><span>内存占用</span></div>
        </div>
      </div>
    </div>

    <div class="rcq-counters" style="grid-template-columns:repeat(4,1fr)">
      <div class="rcq-ct"><b>{{ cnt.groups || 0 }}</b><span>群聊</span></div>
      <div class="rcq-ct"><b>{{ cnt.friends || 0 }}</b><span>好友</span></div>
      <div class="rcq-ct"><b>{{ cnt.sessions || 0 }}</b><span>会话</span></div>
      <div class="rcq-ct"><b>{{ cnt.messages || 0 }}</b><span>消息</span></div>
    </div>

    <div class="rcq-pnl">
      <div class="rcq-ph"><b>RainCough Bot</b><span class="sp"></span>
        <span class="rcq-lamp" v-if="botst"><b :class="botst.onebot && botst.onebot.connected ? 'on' : 'off'"></b>
          {{ botst.onebot && botst.onebot.connected ? '已连 SnowLuma' : '未连接' }}</span>
        <span class="rcq-lamp" v-else><b class="off"></b>rcbot 未运行</span>
      </div>
      <div class="rcq-row2" style="margin-top:0">
        <div class="rcq-fld"><span class="k">提供商</span><span class="v">{{ (botst && botst.provider) || '—' }}</span></div>
        <div class="rcq-fld"><span class="k">模型</span><span class="v">{{ (botst && botst.provider_model) || '—' }}</span></div>
        <div class="rcq-fld"><span class="k">会话</span><span class="v">{{ botst && botst.stats ? botst.stats.sessions : '—' }} 个 / 消息 {{ botst && botst.stats ? fmtNum(botst.stats.messages) : '—' }} 条</span></div>
        <div class="rcq-fld"><span class="k">上下文</span><span class="v">{{ (botst && botst.context && botst.context.max_tokens) ? (botst.context.max_tokens + ' tokens 窗口') : '—' }}</span></div>
      </div>
      <div class="rcq-fld" style="margin-top:10px" v-if="botst && botst.last_error">
        <span class="k">最近错误</span>
        <span class="v rcq-err" :title="botst.last_error">{{ botst.last_error }}</span>
      </div>
    </div>
  </div>`,
}

// ------------------------------------------------------------------ QQ 账户（SnowLuma 单后端）
//
// 一个 QQ 号 = 一个 SnowLuma 容器（Docker）。框架没有二维码 API，
// 登录只能在内嵌的 noVNC 远程桌面里完成 —— 所以这里不再有二维码图片、
// 「刷新二维码」、后端切换下拉与快登按钮。

const Accounts = {
  data() {
    return {
      S,
      acc: null,
      busy: '', err: '', vncBusy: false,
      loginOpen: false, msg: '', vncErr: '',
      novncUrl: '', novncPw: '',
    }
  },
  computed: {
    login() { return !!(this.acc && this.acc.login) },
    ready() { return !!(this.acc && this.acc.core_ready) },
    online() { return !!(this.acc && (this.acc.online || this.acc.connected)) },
    uin() { return (this.acc && this.acc.uin) || '' },
    nick() { return (this.acc && this.acc.nick) || '' },
    avatar() {
      if (this.acc && this.acc.avatar) return this.acc.avatar
      const u = this.uin
      if (!/^\d{5,12}$/.test(u)) return ''
      return 'https://q1.qlogo.cn/g?b=qq&nk=' + u + '&s=100'
    },
    statusText() {
      if (!this.acc) return '未知'
      if (this.online && this.ready) return '已登录'
      if (this.acc.login) return '已登录（初始化中）'
      const st = this.acc.state || ''
      if (st === 'failed') return '启动失败'
      if (st === 'inactive' || st === 'exited') return '已停止'
      if (st === 'active' || st === 'running') return '运行中（未登录）'
      if (st === 'absent') return '未部署'
      return st || '未知'
    },
    statusCls() {
      if (this.online && this.ready) return 'ok'
      if (this.acc && this.acc.state === 'failed') return 'off'
      return ''
    },
  },
  async mounted() {
    await this.load()
    this.timer = setInterval(() => this.load(true), 5000)
  },
  beforeUnmount() { if (this.timer) clearInterval(this.timer) },
  methods: {
    async load(silent) {
      if (!silent) this.busy = 'load'
      try {
        this.acc = await callData('qqbot.account.info')
        this.err = (this.acc && this.acc.error) || ''
        if (this.loginOpen && this.acc && !this.acc.login) this.pollStatus(0)
      } catch (e) {
        this.err = errText(e)
      } finally {
        this.busy = ''
      }
    },
    // noVNC 地址：主机名用当前页面的（后端不知道面板对外的 IP），
    // 端口与路径由后端给（含远程桌面密码，打开即自动连）
    buildNovnc(d) {
      if (!d || !d.novnc_path) return ''
      let host = location.hostname
      if (!host || host === 'localhost') host = '127.0.0.1'
      return location.protocol + '//' + host + ':' + (d.novnc_port || 6081) + d.novnc_path
    },
    async showLogin() {
      this.vncBusy = true
      this.vncErr = ''
      this.msg = ''
      this.novncUrl = ''
      this.loginOpen = true
      try {
        const d = await callData('qqbot.account.qrcode', {})
        if (d && d.login) {
          this.msg = '已经登录了：' + (d.nick || d.uin)
          await this.load(true)
          return
        }
        this.novncUrl = this.buildNovnc(d || {})
        this.novncPw = (d && d.novnc_password) || ''
        if (!this.novncUrl) this.vncErr = '远程桌面地址没拼出来（缺 noVNC 端口或路径）'
        this.pollStatus(0)
      } catch (e) {
        this.vncErr = errText(e)
      } finally {
        this.vncBusy = false
      }
    },
    pollStatus(n) {
      if (n > 100 || !this.loginOpen) return
      setTimeout(async () => {
        if (!this.loginOpen) return
        try {
          const d = await callData('qqbot.account.status', {})
          if (d && d.done) {
            this.msg = '登录成功：' + (d.nick || d.uin) + '（' + d.uin + '）'
            toast('已登录 ' + d.uin, 'ok')
            await this.load(true)
            setTimeout(() => { this.loginOpen = false }, 1200)
            return
          }
          if (d && d.error) this.msg = d.error
          else if (d && d.phase === 'waiting_qrcode') this.msg = '请在远程桌面里用手机 QQ 扫码…'
        } catch (e) {
          this.msg = errText(e)
        }
        this.pollStatus(n + 1)
      }, 3000)
    },
    async act(action) {
      this.busy = action
      try {
        const msg = {
          start: '已启动', stop: '已停止', restart: '已重启', logout: '已退出登录',
        }[action] || '已执行'
        if (action === 'logout' && !confirm('退出登录会清掉本机的登录态，下次要重新扫码。确定？')) return
        await call('qqbot.account.action', { action })
        toast(msg, 'ok')
        this.loginOpen = false
        await this.load(true)
      } catch (e) {
        toast(errText(e), 'err')
      } finally {
        this.busy = ''
      }
    },
    closeLogin() {
      this.loginOpen = false
      this.msg = ''
      this.novncUrl = ''
      this.vncErr = ''
    },
  },
  template: `
  <div>
    <div v-if="err" class="rcq-pnl rcq-warn" style="font-size:12px">{{ err }}</div>

    <div class="rcq-pnl">
      <div class="rcq-ph">
        <b>QQ 账户</b>
        <span class="rcq-hint">SnowLuma · 单账户</span>
        <span class="sp"></span>
        <button class="btn btn-sm btn-primary" :disabled="vncBusy" @click="showLogin()">
          {{ vncBusy ? '准备中…' : (login ? '重新登录' : '扫码登录') }}
        </button>
        <button class="btn btn-sm" :disabled="!!busy" @click="load()">刷新</button>
      </div>

      <div class="rcq-acct" style="padding:16px">
        <img class="rcq-ava" :src="avatar" alt="" v-if="avatar" />
        <div class="rcq-ava" v-else></div>
        <div style="min-width:0;flex:1">
          <div class="rcq-nick">
            {{ nick || (uin ? 'QQ ' + uin : '未登录') }}
            <span class="rcq-pill" :class="statusCls">{{ statusText }}</span>
          </div>
          <div class="rcq-uin">{{ uin || '还没有登录 QQ 账号' }}</div>
        </div>
      </div>

      <div class="rcq-iacts" style="margin-top:12px">
        <button class="btn btn-sm" :disabled="!!busy" @click="act('start')">启动</button>
        <button class="btn btn-sm" :disabled="!!busy" @click="act('restart')">重启</button>
        <button class="btn btn-sm" :disabled="!!busy" @click="act('stop')">停止</button>
        <button class="btn btn-sm" :disabled="!!busy || !login" @click="act('logout')">退出登录</button>
      </div>

      <div v-if="loginOpen" class="rcq-scan">
        <div class="rcq-vncbar">
          <b>远程桌面</b>
          <span class="rcq-hint">在下面的画面里用手机 QQ 扫码登录</span>
          <span class="sp"></span>
          <a v-if="novncUrl" :href="novncUrl" target="_blank" rel="noopener"
            class="btn btn-sm">新窗口打开</a>
          <button class="btn btn-sm" @click="closeLogin()">关闭</button>
        </div>
        <div v-if="novncUrl" class="rcq-vncwrap">
          <iframe :src="novncUrl" class="rcq-vnc" allow="clipboard-read; clipboard-write"
            referrerpolicy="no-referrer"></iframe>
        </div>
        <div v-else class="rcq-empty2">
          {{ vncErr || (vncBusy ? '正在启动容器与远程桌面…' : '远程桌面还没准备好') }}
        </div>
        <div class="rcq-note" style="display:block;margin-top:8px">
          画面是 SnowLuma 容器里的 QQ 桌面，可以直接用鼠标操作。
          <br />
          <b>如果二维码显示「已过期」，点画面里那个「刷新」按钮</b>；
          首次启动要等 10~30 秒容器起来。
          <br />
          如果这里是空白，说明浏览器不允许内嵌 —— 点右上角「新窗口打开」。
          <template v-if="novncPw">
            <br />远程桌面密码：<code>{{ novncPw }}</code>（新窗口打开时可能要输）
          </template>
        </div>
        <div v-if="msg" style="margin-top:8px;font-size:12px">{{ msg }}</div>
      </div>

      <div class="rcq-note" style="margin-top:14px">
        本插件是单账户模式：只管理一个 QQ 号。
        <br />
        <b>SnowLuma</b> 把 QQ 整包跑在 Docker 里，登录要在内嵌的远程桌面里扫码
        （QQ 客户端自己画二维码，没有 API 能单独取出来）。
        <br />
        换号时点「退出登录」清掉登录态，再重新扫码即可。
      </div>
    </div>
  </div>`,
}

// ------------------------------------------------------------------ 聊天记录
// ------------------------------------------------------------------ 媒体库
const MediaLib = {
  components: { ThumbImg },
  data() {
    return {
      S, items: [], stats: null, total: 0,
      kind: '', sender: '', kw: '', sort: 'time', moreOpen: false,
      limit: 60, offset: 0, hasMore: false,
      busy: '', err: '', light: '', lightKind: '',
      picked: {}, job: null, jobTimer: null,
    }
  },
  computed: {
    kindStats() {
      const m = {}
      for (const s of ((this.stats || {}).items || [])) m[s.kind] = s
      return m
    },
    totalBytes() { return ((this.stats || {}).total_bytes) || 0 },
    totalFiles() { return ((this.stats || {}).total_files) || 0 },
    pickedIds() {
      return Object.keys(this.picked).filter((k) => this.picked[k]).map((k) => Number(k))
    },
    pendingCount() {
      return this.items.filter((x) => x.transcode === 'pending').length
    },
    jobPct() {
      const j = this.job
      if (!j || !j.total) return 0
      return Math.min(100, Math.round((j.done / j.total) * 100))
    },
  },
  async mounted() {
    await this.load()
    this.$nextTick(() => this.setupMore())
  },
  beforeUnmount() {
    if (this._io) { this._io.disconnect(); this._io = null }
    if (this.jobTimer) { clearInterval(this.jobTimer); this.jobTimer = null }
  },
  methods: {
    fmtFull, fmtNum,
    mediaAlive,
    setupMore() {
      if (typeof IntersectionObserver === 'undefined') return
      const el = this.$refs.moreEl
      if (!el) return
      if (this._io) this._io.disconnect()
      this._io = new IntersectionObserver((es) => {
        if (es.some((e) => e.isIntersecting) && this.hasMore && !this.busy) this.loadMore()
      }, { rootMargin: '300px' })
      this._io.observe(el)
    },
    bytes(n) {
      n = Number(n) || 0
      if (n >= 1073741824) return (n / 1073741824).toFixed(2) + ' G'
      if (n >= 1048576) return (n / 1048576).toFixed(1) + ' M'
      if (n >= 1024) return (n / 1024).toFixed(0) + ' K'
      return n + ' B'
    },
    mediaUrl(m) { return mediaFileUrl(m) },
    kindLabel(k) {
      return { image: '图片', video: '视频', record: '语音', face: '表情', file: '文件' }[k] || (k || '其它')
    },
    kindIcon(k) {
      return { image: '🖼', video: '🎬', record: '🎤', face: '😀', file: '📎' }[k] || '📄'
    },
    async load(append) {
      this.busy = 'load'
      try {
        const d = await callData('qqbot.chat.media_list', {
          kind: this.kind, sender: this.sender, kw: this.kw, sort: this.sort,
          limit: this.limit, offset: append ? this.offset : 0,
          with_stats: append ? 0 : 1,
        })
        const items = (d && d.items) || []
        this.items = append ? this.items.concat(items) : items
        this.stats = (d && d.stats) || this.stats
        this.total = (d && d.total) || this.items.length
        this.offset = this.items.length
        this.hasMore = !!(d && d.has_more)
      } catch (e) {
        this.err = errText(e)
      } finally {
        this.busy = ''
        this.$nextTick(() => this.setupMore())
      }
    },
    async reload() { this.offset = 0; this.picked = {}; await this.load(false) },
    setKind(k) { this.kind = k; this.reload() },
    clearFilters() { this.kind = ''; this.sender = ''; this.kw = ''; this.reload() },
    // 清理媒体副本（原「聊天记录」页的能力，合并到媒体库）
    async purgeAll() {
      if (!confirm('清理媒体副本？\n\n只删图片/语音/视频这些媒体文件，聊天记录文字一条不删。')) return
      this.busy = 'purge'
      try {
        const r = await callData('qqbot.chat.purge_media', { confirm: true })
        toast('已清理 ' + ((r && r.files) || 0) + ' 个文件，释放 ' + this.bytes((r && r.bytes) || 0), 'ok')
        await this.reload()
      } catch (e) {
        toast(errText(e), 'err')
      } finally {
        this.busy = ''
      }
    },
    async loadMore() { await this.load(true) },
    toggle(id) { this.picked[id] = !this.picked[id] },
    pickAll() {
      const all = this.items.every((x) => this.picked[x.id])
      const next = {}
      if (!all) for (const x of this.items) next[x.id] = true
      this.picked = next
    },
    open(m) {
      this.lightKind = m.kind
      this.light = this.mediaUrl(m)
    },
    async transcode() {
      const ids = this.pickedIds.length ? this.pickedIds : null
      if (!ids && !confirm('把媒体库里所有「浏览器放不了」的视频/语音转成可播放格式？\n\n转换在后台进行，可以随时取消。')) return
      this.busy = 'transcode'
      try {
        const r = await callData('qqbot.chat.media_transcode', ids ? { ids, async: true } : { async: true })
        if (r && r.job) {
          this.job = { id: r.job, state: 'running', total: r.total || 0, done: 0, ok: 0, failed: 0 }
          this.pollJob()
        } else {
          toast('转码完成：成功 ' + (r.ok || 0) + '，失败 ' + (r.failed || 0), 'ok')
          await this.reload()
        }
      } catch (e) {
        toast(errText(e), 'err')
      } finally {
        this.busy = ''
      }
    },
    pollJob() {
      if (this.jobTimer) clearInterval(this.jobTimer)
      this.jobTimer = setInterval(async () => {
        if (!this.job) { clearInterval(this.jobTimer); this.jobTimer = null; return }
        try {
          const d = await callData('qqbot.chat.media_task', { id: this.job.id })
          if (d) this.job = Object.assign({}, this.job, d)
          if (this.job.state !== 'running') {
            clearInterval(this.jobTimer); this.jobTimer = null
            toast('转码' + (this.job.state === 'cancelled' ? '已取消' : '完成')
              + '：成功 ' + this.job.ok + '，失败 ' + this.job.failed, 'ok')
            setTimeout(() => { this.job = null; this.reload() }, 1200)
          }
        } catch (e) { /* 下一轮再试 */ }
      }, 1200)
    },
    async cancelJob() {
      if (!this.job) return
      try { await callData('qqbot.chat.media_task', { id: this.job.id, cancel: true }) } catch (e) {}
    },
    async remove() {
      const ids = this.pickedIds
      if (!ids.length) { toast('先勾选要删除的媒体', 'err'); return }
      if (!confirm('删除选中的 ' + ids.length + ' 个媒体文件？\n\n磁盘上的文件会真的删掉，聊天记录里的位置会变成「已失效」。')) return
      this.busy = 'del'
      try {
        const r = await callData('qqbot.chat.media_delete', { ids, confirm: true })
        toast('已删除 ' + (r.files || 0) + ' 个文件，释放 ' + this.bytes(r.bytes || 0), 'ok')
        await this.reload()
      } catch (e) {
        toast(errText(e), 'err')
      } finally {
        this.busy = ''
      }
    },
    async reindex() {
      this.busy = 'reindex'
      try {
        const r = await callData('qqbot.chat.media_reindex', {})
        toast('已重建索引：' + (r.indexed || 0) + ' 个媒体'
          + (r.cleaned ? '，清理僵尸 ' + r.cleaned : ''), 'ok')
        await this.reload()
      } catch (e) {
        toast(errText(e), 'err')
      } finally {
        this.busy = ''
      }
    },
    // 修复引用：转码后文件改名了，消息里还指向旧名 → 前端取不到文件
    async repair() {
      this.busy = 'repair'
      try {
        const r = await callData('qqbot.chat.media_repair', {})
        toast('已修复 ' + (r.fixed || 0) + ' 条消息的媒体引用', 'ok')
        await this.reload()
      } catch (e) {
        toast(errText(e), 'err')
      } finally {
        this.busy = ''
      }
    },
  },
  template: `
  <div @click="moreOpen = false">
    <div v-if="err" class="rcq-pnl rcq-warn" style="font-size:12px">{{ err }}</div>

    <div class="rcq-pnl">
      <div class="rcq-flex" style="gap:6px">
        <button class="btn btn-sm" :class="kind === '' ? 'btn-primary' : ''" @click="setKind('')">
          全部 {{ fmtNum(totalFiles) }} 个 · {{ bytes(totalBytes) }}</button>
        <button v-for="s in (stats || {}).items || []" :key="s.kind" class="btn btn-sm"
          :class="kind === s.kind ? 'btn-primary' : ''" @click="setKind(s.kind)">
          {{ kindLabel(s.kind) }} {{ fmtNum(s.count) }} · {{ bytes(s.bytes) }}</button>
        <span style="margin-left:auto"></span>
        <button class="btn btn-sm" :disabled="!!busy" @click="reindex">重建索引</button>
        <button class="btn btn-sm" :disabled="!!busy" @click="repair">修复引用</button>
        <button class="btn btn-sm" :disabled="!!busy || !!(job && job.state === 'running')" @click="transcode">
          {{ (job && job.state === 'running') ? ('转码中 ' + job.done + '/' + job.total) : '转成可播放格式' }}
        </button>
        <div class="rcq-more">
          <button class="btn btn-sm" @click.stop="moreOpen = !moreOpen">更多 ▾</button>
          <div v-if="moreOpen" class="rcq-more-pop" @click.stop>
            <button :disabled="!pickedIds.length" @click="remove(); moreOpen = false">
              删除选中{{ pickedIds.length ? '（' + pickedIds.length + '）' : '' }}</button>
            <button @click="purgeAll(); moreOpen = false">清理媒体副本</button>
          </div>
        </div>
      </div>
      <div class="rcq-note">
        点击上面的类型可以筛选；「转成可播放格式」在后台转码，可随时取消。
        QQ 的视频多是 HEVC、语音是 AMR，浏览器放不了 —— 转完变成 H.264 / mp3。
      </div>
    </div>

    <div v-if="job" class="rcq-pnl">
      <div class="rcq-flex">
        <b>后台转码 {{ job.done }}/{{ job.total }}</b>
        <span class="rcq-hint">成功 {{ job.ok }} · 失败 {{ job.failed }}</span>
        <span style="margin-left:auto"></span>
        <button v-if="job.state === 'running'" class="btn btn-sm" @click="cancelJob">取消</button>
      </div>
      <div class="rcq-bar2" style="margin-top:8px"><i :style="{ width: jobPct + '%' }"></i></div>
    </div>

    <div class="rcq-pnl">
      <div class="rcq-grid">
        <label class="rcq-fi">
          <span>发送者</span>
          <input class="input" v-model="sender" placeholder="QQ 号或昵称" @keyup.enter="reload()" />
        </label>
        <label class="rcq-fi">
          <span>文件名关键词</span>
          <input class="input" v-model="kw" placeholder="文件名" @keyup.enter="reload()" />
        </label>
        <label class="rcq-fi">
          <span>排序</span>
          <select class="input" v-model="sort" @change="reload()">
            <option value="time">按时间（新→旧）</option>
            <option value="size">按大小（大→小）</option>
            <option value="kind">按类型</option>
          </select>
        </label>
        <div class="rcq-fld rcq-hit"><span class="k">命中</span>
          <span class="v">{{ fmtNum(total) }} 个</span></div>
        <div class="rcq-acts">
          <button class="btn btn-sm btn-primary" :disabled="!!busy" @click="reload">筛选</button>
          <button class="btn btn-sm" @click="clearFilters">清空</button>
        </div>
      </div>
    </div>

    <div v-if="busy === 'load' && !items.length" class="rcq-mlib">
      <div v-for="i in 12" :key="'sk' + i" class="rcq-mcard skel"><div class="th"></div><div class="meta"><div class="n"></div><div class="s"></div></div></div>
    </div>
    <div v-else-if="!items.length" class="rcq-empty2">还没有媒体文件</div>
    <div v-else class="rcq-mlib">
      <div v-for="m in items" :key="m.id" class="rcq-mcard"
        :class="{ on: picked[m.id], gone: !m.exists }">
        <label class="ck" @click.stop>
          <input type="checkbox" :checked="!!picked[m.id]" @change="toggle(m.id)" />
        </label>
        <div class="th" @click="m.exists ? open(m) : null">
          <thumb-img v-if="m.exists && (m.kind === 'image' || m.kind === 'face')" :rel="m.rel" :size="360" />
          <!-- preload="metadata"：只取 moov + 首帧，能显示缩略图又不会拉整个视频 -->
          <video v-else-if="m.exists && m.kind === 'video'" :src="mediaUrl(m)" preload="metadata"
            muted playsinline></video>
          <span v-if="m.exists && m.kind === 'video'" class="vid-ic">▶</span>
          <div v-else class="ph">{{ kindIcon(m.kind) }}</div>
          <span v-if="m.transcode === 'pending'" class="rcq-badge warn">转码中</span>
          <span v-else-if="m.transcode === 'failed'" class="rcq-badge bad">格式不支持</span>
          <span v-else-if="!m.exists" class="rcq-badge bad">已丢失</span>
        </div>
        <div class="meta">
          <div class="n">{{ kindLabel(m.kind) }} · {{ bytes(m.bytes) }}</div>
          <div class="s">{{ m.sender_name || m.sender_id || '未知' }}</div>
          <div class="t">{{ fmtFull(m.created_at) }}</div>
        </div>
        <a class="dl" v-if="m.exists" :href="mediaUrl(m)" download>下载</a>
        <span class="dl gone" v-else>文件已丢失</span>
      </div>
    </div>
    <div v-if="hasMore" ref="moreEl" class="rcq-loadmore" @click="loadMore()">
      {{ busy ? '加载中…' : '加载更多' }}</div>

    <div v-if="pickedIds.length" class="rcq-batch">
      <b>已选 {{ pickedIds.length }} 项</b>
      <button class="btn btn-sm" @click="pickAll()">
        {{ pickedIds.length === items.length && items.length ? '取消全选' : '全选本页' }}</button>
      <button class="btn btn-sm btn-primary" :disabled="!!busy || !!(job && job.state === 'running')"
        @click="transcode">转码选中</button>
      <button class="btn btn-sm btn-danger" :disabled="!!busy" @click="remove">删除</button>
      <button class="btn btn-sm" @click="picked = {}">取消选择</button>
    </div>

    <div v-if="light" class="rcq-light" @click="light = ''">
      <button class="x" @click.stop="light = ''">×</button>
      <img v-if="lightKind === 'image' || lightKind === 'face'" :src="light" alt="" />
      <video v-else-if="lightKind === 'video'" :src="light" controls autoplay
        style="max-width:100%;max-height:100%"></video>
      <audio v-else-if="lightKind === 'record'" :src="light" controls autoplay
        style="width:min(520px,90vw)"></audio>
      <a v-else :href="light" download style="color:#fff">下载文件</a>
    </div>
  </div>`,
}

// ------------------------------------------------------------------ 查询
const Query = {
  components: { ThumbImg },
  data() {
    return {
      S, items: [], senders: [], total: 0,
      sender: '', recalled: '', kind: '', kw: '',
      limit: 50, beforeId: 0, more: false,
      busy: '', err: '', light: '', lightKind: '', lastMs: 0,
      showSenders: false,
    }
  },
  computed: {
    filtersOn() {
      return !!(this.sender || this.recalled || this.kind || this.kw)
    },
    // 撤回状态：'' 全部 / 'yes' 已撤回 / 'no' 未撤回
    recalledOpts() {
      return [
        { v: '', t: '全部' },
        { v: 'no', t: '未撤回' },
        { v: 'yes', t: '已撤回' },
      ]
    },
    kindOpts() {
      return [
        { v: '', t: '全部' },
        { v: 'text', t: '文本' },
        { v: 'image', t: '图片' },
        { v: 'video', t: '视频' },
        { v: 'record', t: '语音' },
        { v: 'face', t: '表情' },
        { v: 'file', t: '文件' },
      ]
    },
    suggest() {
      const s = String(this.sender || '').trim().toLowerCase()
      if (!s) return []
      return this.senders.filter((x) => {
        const id = String(x.sender_id || '')
        const nm = String(x.sender_name || '')
        return id.indexOf(s) >= 0 || nm.toLowerCase().indexOf(s) >= 0
      }).slice(0, 8)
    },
  },
  async mounted() {
    await this.search(false)
    this.$nextTick(() => this.setupMore())
  },
  beforeUnmount() { if (this._io) { this._io.disconnect(); this._io = null } },
  methods: {
    fmtFull, fmtNum,
    mediaAlive,
    setupMore() {
      if (typeof IntersectionObserver === 'undefined') return
      const el = this.$refs.moreEl
      if (!el) return
      if (this._io) this._io.disconnect()
      this._io = new IntersectionObserver((es) => {
        if (es.some((e) => e.isIntersecting) && this.more && !this.busy) this.loadMore()
      }, { rootMargin: '300px' })
      this._io.observe(el)
    },
    bytes(n) {
      n = Number(n) || 0
      if (n >= 1048576) return (n / 1048576).toFixed(1) + ' M'
      if (n >= 1024) return (n / 1024).toFixed(0) + ' K'
      return n + ' B'
    },
    mediaUrl(m) { return mediaFileUrl(m) },
    kindLabel(k) {
      return { image: '图片', video: '视频', record: '语音', face: '表情', file: '文件' }[k] || (k || '其它')
    },
    async loadSenders(kw) {
      try {
        const d = await callData('qqbot.chat.senders', { kw: kw || '', limit: 20 })
        this.senders = (d && d.items) || []
      } catch (e) { /* 补全拿不到不影响查询 */ }
    },
    // 补全改成「聚焦/输入时按前缀查 20 条」：原来一进页就拉 200 条 + 200 个头像
    onSenderFocus() { this.showSenders = true; this.loadSenders(this.sender) },
    onSenderInput() {
      this.showSenders = true
      clearTimeout(this._st)
      this._st = setTimeout(() => this.loadSenders(this.sender), 250)
    },
    async search(append) {
      this.busy = 'search'
      const t0 = performance.now()
      try {
        const d = await callData('qqbot.chat.query', {
          sender: this.sender,
          recalled: this.recalled,
          kind: this.kind,
          kw: this.kw,
          limit: this.limit,
          before_id: append ? this.beforeId : 0,
        })
        const items = (d && d.items) || []
        this.items = append ? this.items.concat(items) : items
        this.total = (d && d.total !== undefined) ? d.total : this.items.length
        this.beforeId = items.length ? items[items.length - 1].id : 0
        this.more = !!(d && d.has_more)
        this.lastMs = Math.round(performance.now() - t0)
      } catch (e) {
        this.err = errText(e)
      } finally {
        this.busy = ''
        this.$nextTick(() => this.setupMore())
      }
    },
    async reload() { this.beforeId = 0; await this.search(false) },
    async loadMore() { await this.search(true) },
    pickSender(x) {
      this.sender = x.sender_id || x.sender_name || ''
      this.showSenders = false
      this.reload()
    },
    clearFilters() {
      this.sender = ''; this.recalled = ''; this.kind = ''; this.kw = ''
      this.reload()
    },
    openMedia(m) {
      this.lightKind = m.kind
      this.light = this.mediaUrl(m)
    },
    // 这条消息里有哪些媒体类型（用于结果行上的标签）
    kindsOf(m) {
      const out = []
      for (const md of (m.media || [])) {
        const k = md.kind || ''
        if (k && out.indexOf(k) < 0) out.push(k)
      }
      return out
    },
  },
  template: `
  <div>
    <div v-if="err" class="rcq-pnl rcq-warn" style="font-size:12px">{{ err }}</div>

    <div class="rcq-pnl">
      <div class="rcq-grid">
        <label class="rcq-fi" style="position:relative">
          <span>QQ 用户</span>
          <input class="input" v-model="sender" placeholder="QQ 号或昵称"
            @focus="onSenderFocus" @input="onSenderInput" @keyup.enter="reload()" />
          <div v-if="showSenders && suggest.length" class="rcq-sugg">
            <div v-for="x in suggest" :key="x.sender_id" class="rcq-sugg-i"
              @click="pickSender(x)">
              <img v-if="x.avatar" :src="x.avatar" alt="" />
              <b>{{ x.sender_name || x.sender_id }}</b>
              <span>{{ x.sender_id }}</span>
              <i>{{ x.c }} 条</i>
            </div>
          </div>
        </label>

        <label class="rcq-fi" style="margin:0">
          <span>撤回状态</span>
          <select class="input" v-model="recalled" @change="reload()">
            <option v-for="o in recalledOpts" :key="o.v" :value="o.v">{{ o.t }}</option>
          </select>
        </label>

        <label class="rcq-fi" style="margin:0">
          <span>消息类型</span>
          <select class="input" v-model="kind" @change="reload()">
            <option v-for="o in kindOpts" :key="o.v" :value="o.v">{{ o.t }}</option>
          </select>
        </label>

        <label class="rcq-fi" style="margin:0">
          <span>关键词</span>
          <input class="input" v-model="kw" placeholder="消息内容" @keyup.enter="reload()" />
        </label>

        <div class="rcq-acts">
          <button class="btn btn-sm" :disabled="!filtersOn" @click="clearFilters">清空条件</button>
          <button class="btn btn-sm btn-primary" :disabled="!!busy" @click="reload">
            {{ busy === 'search' ? '查询中…' : '查询' }}
          </button>
        </div>
      </div>
      <div class="rcq-note">
        各个条件可以叠加使用 —— 比如「查某个 QQ 号的、已撤回的视频」。
        撤回状态、消息类型、QQ 用户、关键词是「与」的关系。
      </div>
    </div>

    <div class="rcq-pnl" v-if="items.length || total">
      <div class="rcq-flex">
        <b>命中 {{ fmtNum(total) }} 条</b>
        <span class="rcq-hint" v-if="lastMs">耗时 {{ lastMs }}ms</span>
        <span style="margin-left:auto"></span>
        <span class="rcq-hint">已加载 {{ items.length }} 条</span>
      </div>
    </div>

    <div v-if="busy === 'search' && !items.length" class="rcq-qres">
      <div v-for="i in 6" :key="'qsk' + i" class="rcq-qrow skel">
        <div class="hd"><span class="ava-sk"></span><span class="ln-sk w40"></span></div>
        <div class="bd"><span class="ln-sk w80"></span><span class="ln-sk w60"></span></div>
      </div>
    </div>
    <div v-else-if="!items.length" class="rcq-empty2">
      没有符合条件的消息
    </div>

    <div class="rcq-qres">
      <div v-for="m in items" :key="m.id" class="rcq-qrow"
        :class="{ rec: m.recalled }">
        <div class="hd">
          <img v-if="m.sender_avatar || m.sender_id" class="ava" loading="lazy"
            :src="m.sender_avatar || ('https://q1.qlogo.cn/g?b=qq&nk=' + m.sender_id + '&s=100')"
            alt="" />
          <b>{{ m.sender_name || m.sender_id }}</b>
          <span class="tt">{{ fmtFull(m.created_at) }}</span>
          <span class="rcq-badge" v-if="m.recalled">已撤回</span>
          <span class="rcq-badge" v-for="k in kindsOf(m)" :key="k">{{ kindLabel(k) }}</span>
          <span class="rcq-badge plain" v-if="m.kind === 'group'">群 {{ m.target_id }}</span>
          <span class="rcq-badge plain" v-else>私聊 {{ m.target_id }}</span>
        </div>
        <div class="bd">
          <span v-if="m.text && m.text !== '[一条消息被撤回]'">{{ m.text }}</span>
          <span v-else-if="m.text" style="color:var(--f);font-style:italic">{{ m.text }}</span>
          <div class="rcq-media">
            <template v-for="md in (m.media || [])" :key="md.seg">
              <thumb-img v-if="md.kind === 'image' && mediaAlive(md)" :rel="md.rel" :size="320"
                @click="openMedia(md)" style="max-width:150px;max-height:150px;cursor:zoom-in" />
              <thumb-img v-else-if="md.kind === 'face' && mediaAlive(md)" :rel="md.rel" :size="64"
                style="width:26px;height:26px" />
              <video v-else-if="md.kind === 'video' && mediaAlive(md)" controls preload="metadata"
                :src="mediaUrl(md)" style="max-width:240px"></video>
              <audio v-else-if="md.kind === 'record' && mediaAlive(md)" controls
                :src="mediaUrl(md)" style="max-width:240px"></audio>
              <a v-else-if="md.local && md.exists !== 0" class="rcq-file"
                :href="mediaUrl(md)" download>
                {{ md.name || (md.kind + ' 文件') }}
              </a>
              <span v-else class="rcq-note">[{{ md.kind }} 已失效]</span>
            </template>
          </div>
        </div>
      </div>
    </div>
    <div v-if="more" ref="moreEl" class="rcq-loadmore" @click="loadMore()">
      {{ busy ? '加载中…' : '加载更多' }}</div>

    <div v-if="light" class="rcq-light" @click="light = ''">
      <button class="x" @click.stop="light = ''">×</button>
      <img v-if="lightKind === 'image' || lightKind === 'face'" :src="light" alt="" />
      <video v-else-if="lightKind === 'video'" :src="light" controls autoplay
        style="max-width:100%;max-height:100%"></video>
      <audio v-else-if="lightKind === 'record'" :src="light" controls autoplay
        style="width:min(520px,90vw)"></audio>
      <a v-else :href="light" download style="color:#fff">下载文件</a>
    </div>
  </div>`,
}

// ------------------------------------------------------------------ 角色卡片

const Cards = {
  data() {
    return {
      S, list: [], def: '', cur: null, busy: '', err: '', dirty: false,
      section: 'memory', providers: [],
      mem: null, memLoading: false, memSel: null, memDrag: null, memMoved: false,
      memoryOpen: false, showJunk: false,
      memQuery: '', memHits: [], memTimer: null,
      memTiles: {}, memExtra: [], tileTimer: null,
      memStats: null, showStats: false, hitIndex: 0,
      memScopeKey: 'global', memScopes: { groups: [], privates: [] },
      showKeywords: false, kwList: [], kwQuery: '', kwLimit: 80,
      kwNew: { match: '', reply: '', mode: 'contains', require_at: true },
      memView: { s: 0.8, ox: 0, oy: 0 },
    }
  },
  computed: {
    isNew() { return !!(this.cur && this.cur.__new) },
    // 预览用的气泡背景色（主题色 / 气泡色）
    themeColor() { return (this.cur && this.cur.style && this.cur.style.color) || '' },
    provName(pid) {
      const p = this.providers.find((x) => x.id === pid)
      return p ? (p.name || p.id) : (pid || '（跟随账号默认）')
    },
  },
  async mounted() {
    await this.load()
    this.loadScopes()
    try {
      const p = await callData('rcbot.providers')
      this.providers = (p && p.items) || []
    } catch (e) { /* 没有提供商也不影响编辑 */ }
  },
  methods: {
    fmtNum,
    cloneDeep(o) { return JSON.parse(JSON.stringify(o || {})) },
    // 没有封面图时，按名字生成一个稳定的渐变，卡片不至于灰扑扑的
    grad(name) {
      const t = String(name || '')
      let h = 0
      for (let i = 0; i < t.length; i++) h = (h * 31 + t.charCodeAt(i)) % 360
      return 'linear-gradient(135deg, hsl(' + h + ' 58% 56%), hsl(' + ((h + 46) % 360) + ' 52% 42%))'
    },
    coverStyle(c) {
      const cover = (c && c.cover_url) || (/^https?:/i.test((c && c.cover) || '') ? c.cover : '')
      return cover ? { backgroundImage: 'url(' + cover + ')' } : { backgroundImage: this.grad((c || {}).name) }
    },
    avatarSrc(c) {
      if (!c) return ''
      return c.avatar_url || (/^https?:/i.test(c.avatar || '') ? c.avatar : '')
    },
    // 图片字段有两种来源：
    //   c.cover        —— 卡片里存的原始值（相对媒体目录，可移植）
    //   c.cover_url    —— 后端算好的预览地址（本地托管的图片走这条）
    // 优先用 *_url，没有再退回原值（外链时两者一样）。
    assetSrc(c, key) {
      if (!c) return ''
      return c[key + '_url'] || c[key] || ''
    },
    async load() {
      this.busy = 'load'
      try {
        const d = await callData('rcbot.cards')
        this.list = (d && d.items) || []
        this.def = (d && d.default) || ''
        if (!this.cur || this.cur.__new) {
          // 刷新后停在卡片列表，不自动进入某张卡的记忆
          this.cur = null
          this.memoryOpen = false
        } else {
          const same = this.list.find((x) => x.id === this.cur.id)
          if (same && !this.dirty) this.cur = this.cloneDeep(same)
        }
      } catch (e) { this.err = errText(e) } finally { this.busy = '' }
    },
    pick(c) {
      this.cur = c ? this.cloneDeep(c) : null
      this.dirty = false
      this.memSel = null
      this.memoryOpen = !!this.cur
      this.section = 'memory'
      this.memQuery = ''
      this.memHits = []
      this.memTiles = {}
      this.memExtra = []
      if (this.cur && this.cur.id) this.$nextTick(() => this.loadMemory())
    },
    backToList() {
      this.memoryOpen = false
      this.memSel = null
    },
    add() {
      this.cur = {
        schema: 2, id: '', version: 1, status: 'draft',
        name: '新角色', alias: [], tagline: '', avatar: '', cover: '', portrait: '',
        prompt: '', taboos: [], keywords: [],
        style: { temperature: 0.8, max_tokens: 512, max_chars: 0, allow_emoji: false, color: '' },
        model: { provider_id: '', model: '' },
        context: { keep_rounds: 20 },
        __new: true,
      }
      this.dirty = true
    },
    // ---------------- 数组类字段的编辑辅助
    addGreeting() { if (this.cur) { this.cur.greetings = this.cur.greetings || []; this.cur.greetings.push('') } },
    rmGreeting(i) { if (this.cur && this.cur.greetings) this.cur.greetings.splice(i, 1) },
    addExample() {
      if (!this.cur) return
      this.cur.examples = this.cur.examples || []
      this.cur.examples.push({ user: '', assistant: '' })
    },
    rmExample(i) { if (this.cur && this.cur.examples) this.cur.examples.splice(i, 1) },
    addLore() {
      if (!this.cur) return
      this.cur.lorebook = this.cur.lorebook || []
      this.cur.lorebook.push({ keys: [], content: '' })
    },
    rmLore(i) { if (this.cur && this.cur.lorebook) this.cur.lorebook.splice(i, 1) },
    loreKeys(l) { return (l.keys || []).join('、') },
    setLoreKeys(l, v) { l.keys = String(v || '').split(/[、,，\s]+/).filter(Boolean) },
    addKw() {
      if (!this.cur) return
      this.cur.keywords = this.cur.keywords || []
      this.cur.keywords.push({ match: '', reply: '', mode: 'contains', require_at: true, enabled: true })
      this.dirty = true
    },
    rmKw(i) {
      if (!this.cur || !this.cur.keywords) return
      this.cur.keywords.splice(i, 1)
      this.dirty = true
    },
    taboosText() { return (this.cur && this.cur.taboos || []).join('\n') },
    setTaboosText(v) { if (this.cur) this.cur.taboos = String(v || '').split('\n').map((x) => x.trim()).filter(Boolean) },
    // ---------------- 记忆星空
    memColor(t) {
      const m = { profile: '#e8c46a', appearance: '#5fd0d8', persona: '#b48cf0',
        taboo: '#f08c8c', canon: '#7aa8f0', fact: '#6fd08a', event: '#f0a45f',
        greeting: '#f0d06a', example: '#f08cc8', trigger: '#e05a5a',
        style: '#8a9ab0', model: '#8a9ab0' }
      return m[t] || '#9ab6d0'
    },
    memName(t) {
      const m = { profile: '身份', appearance: '形象', persona: '行为',
        taboo: '禁则', canon: '设定', fact: '事实', event: '事件',
        greeting: '开场白', example: '示例', trigger: '触发',
        style: '风格', model: '模型' }
      return m[t] || '记忆'
    },
    memState(s) {
      return s === 'junk' ? '垃圾场' : s === 'dormant' ? '休眠' : '正常'
    },
    openSection(name) {
      this.section = name
      if (name === 'memory') this.$nextTick(() => this.loadMemory())
    },
    scopeParams() {
      if (!this.memScopeKey || this.memScopeKey === 'global') {
        return { scope_type: 'global', scope_id: '' }
      }
      const i = this.memScopeKey.indexOf(':')
      return { scope_type: this.memScopeKey.slice(0, i), scope_id: this.memScopeKey.slice(i + 1) }
    },
    async loadScopes() {
      try {
        const d = await callData('rcbot.sessions')
        const items = (d && (d.items || d)) || []
        const groups = [], privates = []
        const seen = {}
        for (const x of items) {
          const target = x && (x.target_id || x.target)
          if (!target) continue
          if (x.kind !== 'group' && x.kind !== 'private') continue
          const key = x.kind + ':' + target
          if (seen[key]) continue
          seen[key] = 1
          const label = x.display || x.title || x.name || String(target)
          if (x.kind === 'group') groups.push({ key, label })
          else privates.push({ key, label })
        }
        this.memScopes = { groups, privates }
      } catch (e) { /* 没有会话也不影响全局视图 */ }
    },
    changeScope() {
      this.memSel = null
      this.memHits = []
      this.memExtra = []
      this.loadMemory()
    },
    async loadMemory() {
      if (!this.cur || !this.cur.id) return
      this.memLoading = true
      this.memTiles = {}
      this.memExtra = []
      try {
        const sp = this.scopeParams()
        const d = await callData('rcbot.memory.map', { card_id: this.cur.id, ...sp })
        this.mem = d || null
        this.$nextTick(() => { this.fitMem(); this.ensureTiles() })
      } catch (e) { toast(errText(e), 'err') } finally { this.memLoading = false }
    },
    allStars() {
      const out = []
      for (const k in this.memTiles) out.push(...(this.memTiles[k] || []))
      out.push(...(this.memExtra || []))
      return out
    },
    scheduleTiles() {
      clearTimeout(this.tileTimer)
      this.tileTimer = setTimeout(() => this.ensureTiles(), 180)
    },
    async ensureTiles() {
      const c = this.$refs.memCanvas
      if (!c || !this.cur || !this.mem) return
      const w = c.clientWidth || 800, h = c.clientHeight || 520
      const v = this.memView
      const x0 = (0 - v.ox) / v.s, x1 = (w - v.ox) / v.s
      const y0 = (0 - v.oy) / v.s, y1 = (h - v.oy) / v.s
      const tx0 = Math.floor(x0 / 512), tx1 = Math.floor(x1 / 512)
      const ty0 = Math.floor(y0 / 512), ty1 = Math.floor(y1 / 512)
      const jobs = []
      for (let tx = tx0; tx <= tx1 && jobs.length < 6; tx++) {
        for (let ty = ty0; ty <= ty1 && jobs.length < 6; ty++) {
          const key = tx + ',' + ty
          if (this.memTiles[key] !== undefined) continue
          this.memTiles[key] = []
          jobs.push(callData('rcbot.memory.tile', { card_id: this.cur.id, tx, ty, ...this.scopeParams() })
            .then((d) => { this.memTiles[key] = (d && d.items) || [] })
            .catch(() => { this.memTiles[key] = [] }))
        }
      }
      if (jobs.length) {
        await Promise.all(jobs)
        this.drawMem()
      }
    },
    fitMem() {
      const c = this.$refs.memCanvas
      if (!c || !this.mem) return
      const all = (this.mem.main || []).concat(this.allStars())
      if (!all.length) return
      let minx, maxx, miny, maxy
      if (this.mem.bbox) {
        minx = this.mem.bbox.minx; maxx = this.mem.bbox.maxx
        miny = this.mem.bbox.miny; maxy = this.mem.bbox.maxy
      } else {
        const xs = all.map((s) => s.x), ys = all.map((s) => s.y)
        minx = Math.min(...xs); maxx = Math.max(...xs)
        miny = Math.min(...ys); maxy = Math.max(...ys)
      }
      const w = c.clientWidth || 800, h = c.clientHeight || 520
      const s = Math.min(w / (maxx - minx + 140), h / (maxy - miny + 140), 2.4)
      this.memView = { s, ox: w / 2 - (minx + maxx) / 2 * s, oy: h / 2 - (miny + maxy) / 2 * s }
      this.drawMem()
    },
    drawMem() {
      const c = this.$refs.memCanvas
      if (!c) return
      const dpr = window.devicePixelRatio || 1
      const w = c.clientWidth || 800, h = c.clientHeight || 520
      if (c.width !== Math.round(w * dpr) || c.height !== Math.round(h * dpr)) {
        c.width = Math.round(w * dpr); c.height = Math.round(h * dpr)
      }
      const g = c.getContext('2d')
      g.setTransform(dpr, 0, 0, dpr, 0, 0)
      g.clearRect(0, 0, w, h)
      const bg = g.createRadialGradient(w * 0.5, h * 0.42, 10, w * 0.5, h * 0.42, Math.max(w, h) * 0.85)
      bg.addColorStop(0, '#101c31'); bg.addColorStop(0.55, '#0a1220'); bg.addColorStop(1, '#04060b')
      g.fillStyle = bg; g.fillRect(0, 0, w, h)
      // 星云：三团很淡的冷色雾
      const neb = (cx, cy, rad, col) => {
        const rg = g.createRadialGradient(cx, cy, 0, cx, cy, rad)
        rg.addColorStop(0, col); rg.addColorStop(1, 'rgba(0,0,0,0)')
        g.fillStyle = rg; g.fillRect(0, 0, w, h)
      }
      neb(w * 0.18, h * 0.22, Math.max(w, h) * 0.62, 'rgba(46,96,158,.20)')
      neb(w * 0.84, h * 0.72, Math.max(w, h) * 0.58, 'rgba(112,70,156,.16)')
      neb(w * 0.58, h * 0.10, Math.max(w, h) * 0.45, 'rgba(28,120,136,.12)')
      // 远景尘埃
      for (let i = 0; i < 140; i++) {
        const dx = (Math.sin(i * 12.9898) * 43758.5453) % 1
        const dy = (Math.sin(i * 78.233) * 12345.6789) % 1
        const x = Math.abs(dx) * w, y = Math.abs(dy) * h
        g.fillStyle = 'rgba(190,214,245,' + (0.05 + (i % 5) * 0.012) + ')'
        g.fillRect(x, y, 1, 1)
      }
      // 暗角
      const vg = g.createRadialGradient(w * 0.5, h * 0.5, Math.min(w, h) * 0.25,
                                        w * 0.5, h * 0.5, Math.max(w, h) * 0.72)
      vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,0,0,.52)')
      g.fillStyle = vg; g.fillRect(0, 0, w, h)
      if (!this.mem) return
      const v = this.memView
      const p = (s) => [s.x * v.s + v.ox, s.y * v.s + v.oy]
      const byId = {}
      for (const s of (this.mem.main || [])) byId[s.id] = s
      const clusterCount = {}
      for (const cl of (this.mem.clusters || [])) clusterCount[cl.name] = cl.count
      // 主星 → 卫星连线
      g.lineWidth = 0.7
      for (const s of this.allStars()) {
        const m = byId[s.parent]
        if (!m) continue
        const [x1, y1] = p(m), [x2, y2] = p(s)
        g.strokeStyle = 'rgba(120,160,220,' + (0.10 + 0.25 * (s.b || 0.3)) + ')'
        g.beginPath(); g.moveTo(x1, y1); g.lineTo(x2, y2); g.stroke()
      }
      const starPath = (x, y, r, inner, points) => {
        g.beginPath()
        for (let i = 0; i < points * 2; i++) {
          const rr = i % 2 ? inner : r
          const a = -Math.PI / 2 + i * Math.PI / points
          const px = x + Math.cos(a) * rr, py = y + Math.sin(a) * rr
          if (i) g.lineTo(px, py); else g.moveTo(px, py)
        }
        g.closePath()
      }
      const hitSet = new Set((this.memHits || []).map((s) => s.id))
      const searching = !!(this.memQuery || '').trim() && hitSet.size > 0
      const dim = (s) => (searching && !hitSet.has(s.id) ? 0.15 : 1)
      const drawStar = (s) => {
        const [x, y] = p(s)
        if (x < -30 || y < -30 || x > w + 30 || y > h + 30) return
        const b = Math.max(0.08, s.b || 0.3)
        const col = this.memColor(s.type)
        if (s.main) {
          const r = 14 + 8 * b
          g.shadowColor = col
          g.shadowBlur = 26 * b + 10
          g.fillStyle = col
          g.globalAlpha = (0.60 + 0.40 * b) * dim(s)
          starPath(x, y, r, r * 0.40, 5)
          g.fill()
          // 十字星芒
          g.shadowBlur = 0
          g.globalAlpha = 0.50 * b
          g.strokeStyle = col
          g.lineWidth = 1.4
          g.beginPath()
          g.moveTo(x - r * 2.4, y); g.lineTo(x + r * 2.4, y)
          g.moveTo(x, y - r * 2.4); g.lineTo(x, y + r * 2.4)
          g.stroke()
          // 星核
          g.globalAlpha = 0.98
          g.fillStyle = '#ffffff'
          g.beginPath(); g.arc(x, y, Math.max(1.8, r * 0.20), 0, Math.PI * 2); g.fill()
          g.globalAlpha = 0.92
          g.fillStyle = 'rgba(235,244,255,.92)'
          g.font = '13px system-ui, sans-serif'
          g.fillText(this.memName(s.type) + ' · ' + (clusterCount[s.type] || ''), x + r + 8, y + 4)
        } else {
          const r = 2.8 + 5.0 * b
          g.shadowColor = col
          g.shadowBlur = 10 * b + 3
          g.fillStyle = col
          g.globalAlpha = (0.32 + 0.68 * b) * dim(s)
          starPath(x, y, r, r * 0.26, 4)
          g.fill()
          g.globalAlpha = 0.60 * b
          g.fillStyle = '#ffffff'
          g.beginPath(); g.arc(x, y, Math.max(0.8, r * 0.18), 0, Math.PI * 2); g.fill()
        }
        g.shadowBlur = 0
        g.globalAlpha = 1
      }
      for (const s of this.allStars()) {
        // LOD：缩太小的时候先不画暗卫星，放大后再出现
        if (this.memView.s < 0.28 && (s.b || 0.3) < 0.55 && !searching) continue
        if (this.memView.s < 0.16 && !searching) continue
        drawStar(s)
      }
      if (this.showJunk) {
        g.shadowBlur = 0
        const jl = this.mem.junk_stars || []
        g.globalAlpha = 0.55
        g.fillStyle = 'rgba(170,188,210,.8)'
        g.font = '12px system-ui, sans-serif'
        g.fillText('垃圾场 · ' + jl.length, 52, h - 58)
        for (let i = 0; i < jl.length; i++) {
          const jx = 56 + (i % 20) * 16
          const jy = h - 38 + Math.floor(i / 20) * 16
          g.globalAlpha = 0.22
          g.fillStyle = 'rgba(160,178,200,1)'
          starPath(jx, jy, 2.0, 0.7, 4)
          g.fill()
        }
        g.globalAlpha = 1
      }
      for (const s of (this.mem.main || [])) drawStar(s)
      if (searching) {
        g.shadowBlur = 0
        g.strokeStyle = 'rgba(255,220,140,.9)'
        g.lineWidth = 1.2
        for (const s of (this.memHits || [])) {
          const [x, y] = p(s)
          if (x < -20 || y < -20 || x > w + 20 || y > h + 20) continue
          g.beginPath(); g.arc(x, y, 13, 0, Math.PI * 2); g.stroke()
        }
      }
      g.globalAlpha = 1
    },
    toggleJunk() {
      this.$nextTick(() => { this.fitMem(); this.drawMem() })
    },
    searchMem() {
      clearTimeout(this.memTimer)
      this.memTimer = setTimeout(async () => {
        const q = this.memQuery.trim()
        if (!this.cur) return
        if (!q) { this.memHits = []; this.drawMem(); return }
        try {
          const d = await callData('rcbot.memory.search', { card_id: this.cur.id, q, ...this.scopeParams() })
          this.memHits = (d && d.items) || []
          this.hitIndex = 0
          this.memExtra = this.memHits.slice()
          if (this.memHits.length) this.focusHits()
          else this.drawMem()
        } catch (e) { /* 搜索失败不改动星图 */ }
      }, 260)
    },
    async consolidateMem() {
      if (!this.cur) return
      if (!confirm('合并近似重复的记忆，并归档陈旧事件？')) return
      try {
        const r = await callData('rcbot.memory.consolidate', { card_id: this.cur.id })
        toast('记忆已巩固：合并 ' + ((r && r.merged) || 0) + ' 条，归档 ' + ((r && r.stale) || 0) + ' 条', 'ok')
        await this.loadMemory()
        if (this.showStats) this.memStats = await callData('rcbot.memory.stats', { card_id: this.cur.id })
      } catch (e) { toast(errText(e), 'err') }
    },
    async openKeywords() {
      this.showKeywords = true
      this.kwLimit = 80
      await this.loadKeywords()
    },
    async loadKeywords() {
      if (!this.cur) return
      try {
        const d = await callData('rcbot.memory.triggers', { card_id: this.cur.id })
        this.kwList = (d && d.items) || []
      } catch (e) { toast(errText(e), 'err') }
    },
    kwFiltered() {
      const q = (this.kwQuery || '').trim().toLowerCase()
      if (!q) return this.kwList
      return this.kwList.filter((k) => (k.match || '').toLowerCase().includes(q) ||
        (k.reply || '').toLowerCase().includes(q))
    },
    async saveKw(k) {
      if (!k || !k.match || !k.reply) { toast('关键词和回复都不能为空', 'err'); return }
      try {
        await callData('rcbot.memory.save', { item: {
          id: k.id, card_id: this.cur.id, type: 'trigger', mode: 'config',
          content: k.reply, importance: 0.4,
          meta: { match: k.match, reply: k.reply, mode: 'contains',
                  require_at: !!k.require_at, enabled: k.enabled !== false },
        } })
        k.enabled = k.enabled !== false
        toast('已保存：' + k.match, 'ok')
      } catch (e) { toast(errText(e), 'err') }
    },
    async delKw(k) {
      if (!k || !confirm('删除关键词「' + k.match + '」？')) return
      try {
        await callData('rcbot.memory.delete', { id: k.id })
        this.kwList = this.kwList.filter((x) => x.id !== k.id)
        toast('已删除', 'ok')
      } catch (e) { toast(errText(e), 'err') }
    },
    async addKeyword() {
      const n = this.kwNew
      if (!n.match.trim() || !n.reply.trim()) { toast('关键词和回复都要填', 'err'); return }
      try {
        await callData('rcbot.memory.save', { item: {
          card_id: this.cur.id, type: 'trigger', mode: 'config',
          content: n.reply.trim(), importance: 0.4,
          meta: { match: n.match.trim(), reply: n.reply.trim(), mode: 'contains',
                  require_at: !!n.require_at, enabled: true },
        } })
        n.match = ''; n.reply = ''
        await this.loadKeywords()
        toast('已添加', 'ok')
      } catch (e) { toast(errText(e), 'err') }
    },
    async bulkKw(enabled) {
      const list = this.kwFiltered()
      if (!list.length) return
      if (!confirm((enabled ? '启用' : '停用') + '当前筛选的 ' + list.length + ' 条？')) return
      for (const k of list) {
        k.enabled = enabled
        await callData('rcbot.memory.save', { item: {
          id: k.id, card_id: this.cur.id, type: 'trigger', mode: 'config',
          content: k.reply, importance: 0.4,
          meta: { match: k.match, reply: k.reply, mode: k.mode,
                  require_at: !!k.require_at, enabled: enabled },
        } })
      }
      toast('已更新 ' + list.length + ' 条', 'ok')
    },
    async toggleStats() {
      if (!this.cur) return
      this.showStats = !this.showStats
      if (this.showStats) {
        try { this.memStats = await callData('rcbot.memory.stats', { card_id: this.cur.id }) } catch (e) {}
      }
    },
    centerOn(s) {
      const c = this.$refs.memCanvas
      if (!c) return
      const w = c.clientWidth || 800, h = c.clientHeight || 520
      const scale = Math.max(0.8, this.memView.s)
      this.memView = { s: scale, ox: w / 2 - s.x * scale, oy: h / 2 - s.y * scale }
      this.drawMem()
    },
    async openHit(delta) {
      if (!this.memHits.length) return
      const n = this.memHits.length
      this.hitIndex = (this.hitIndex + delta + n) % n
      const s = this.memHits[this.hitIndex]
      this.centerOn(s)
      try { this.memSel = await callData('rcbot.memory.item', { id: s.id }) } catch (e) {}
    },
    async openFirstHit() {
      if (!this.memHits.length) return
      try { this.memSel = await callData('rcbot.memory.item', { id: this.memHits[0].id }) } catch (e) {}
    },
    clearSearch() {
      this.memQuery = ''
      this.memHits = []
      this.memExtra = []
      this.$nextTick(() => this.fitMem())
    },
    focusHits() {      const c = this.$refs.memCanvas
      if (!c || !this.memHits.length) return
      const xs = this.memHits.map((s) => s.x), ys = this.memHits.map((s) => s.y)
      const minx = Math.min(...xs), maxx = Math.max(...xs)
      const miny = Math.min(...ys), maxy = Math.max(...ys)
      const w = c.clientWidth || 800, h = c.clientHeight || 520
      const s = Math.min(w / (maxx - minx + 220), h / (maxy - miny + 220), 2.2)
      this.memView = { s, ox: w / 2 - (minx + maxx) / 2 * s, oy: h / 2 - (miny + maxy) / 2 * s }
      this.drawMem()
    },
    memDown(e) {
      this.memDrag = { x: e.clientX, y: e.clientY, ox: this.memView.ox, oy: this.memView.oy }
      this.memMoved = false
    },
    memMove(e) {
      if (!this.memDrag) return
      const dx = e.clientX - this.memDrag.x, dy = e.clientY - this.memDrag.y
      if (Math.abs(dx) + Math.abs(dy) > 3) this.memMoved = true
      this.memView = { s: this.memView.s, ox: this.memDrag.ox + dx, oy: this.memDrag.oy + dy }
      this.drawMem()
    },
    memUp() { this.memDrag = null; this.scheduleTiles() },
    memWheel(e) {
      e.preventDefault()
      const c = this.$refs.memCanvas
      if (!c) return
      const rect = c.getBoundingClientRect()
      const mx = e.clientX - rect.left, my = e.clientY - rect.top
      const k = e.deltaY < 0 ? 1.12 : 0.89
      const s = Math.min(4, Math.max(0.15, this.memView.s * k))
      const v = this.memView
      this.memView = { s, ox: mx - (mx - v.ox) * (s / v.s), oy: my - (my - v.oy) * (s / v.s) }
      this.drawMem()
      this.scheduleTiles()
    },
    async memClick(e) {
      if (this.memMoved) { this.memMoved = false; return }
      if (!this.mem) return
      const c = this.$refs.memCanvas
      const rect = c.getBoundingClientRect()
      const mx = e.clientX - rect.left, my = e.clientY - rect.top
      let best = null, bd = 14
      const pool = (this.mem.main || []).concat(this.allStars(),
        this.showJunk ? (this.mem.junk_stars || []) : [])
      for (const s of pool) {
        const x = s.x * this.memView.s + this.memView.ox
        const y = s.y * this.memView.s + this.memView.oy
        const d = Math.hypot(x - mx, y - my)
        if (d < bd) { bd = d; best = s }
      }
      if (!best) {
        // 垃圾场暗星：左下角固定区域，点一下也能看
        if (this.showJunk) {
          const hh = c.clientHeight || 520
          if (my > hh - 80 && my < hh - 12 && mx > 44) {
            const col = Math.floor((mx - 56) / 16)
            const row = Math.floor((my - (hh - 42)) / 16)
            if (col >= 0 && col < 20 && row >= 0) {
              const j = (this.mem.junk_stars || [])[row * 20 + col]
              if (j) {
                try { this.memSel = await callData('rcbot.memory.item', { id: j.id }) } catch (e) {}
                return
              }
            }
          }
        }
        return
      }
      try {
        this.memSel = await callData('rcbot.memory.item', { id: best.id })
      } catch (err) { toast(errText(err), 'err') }
    },
    async saveMem() {
      if (!this.memSel) return
      try {
        await callData('rcbot.memory.save', { item: this.memSel })
        toast('记忆已保存', 'ok')
        const id = this.memSel.id
        this.memSel = await callData('rcbot.memory.item', { id })
        this.loadMemory()
      } catch (e) { toast(errText(e), 'err') }
    },
    async pinMem() {      if (!this.memSel) return
      try {
        await callData('rcbot.memory.pin', { id: this.memSel.id, pinned: !this.memSel.pinned })
        this.memSel.pinned = this.memSel.pinned ? 0 : 1
        this.loadMemory()
      } catch (e) { toast(errText(e), 'err') }
    },
    async delMem() {
      if (!this.memSel) return
      if (!confirm('把这条记忆移入垃圾场？')) return
      try {
        await callData('rcbot.memory.delete', { id: this.memSel.id })
        this.memSel = null
        this.loadMemory()
      } catch (e) { toast(errText(e), 'err') }
    },
    // ---------------- 保存 / 其它操作
    async save() {
      if (!this.cur) return
      const c = this.cloneDeep(this.cur)
      if (!String(c.name || '').trim()) { toast('角色名字不能为空', 'err'); return }
      delete c.__new
      this.busy = 'save'
      try {
        const r = await callData('rcbot.card.save', { card: c })
        toast('已保存', 'ok')
        this.dirty = false
        this.cur = null
        await this.load()
        if (r && r.id) this.pick(this.list.find((x) => x.id === r.id) || null)
      } catch (e) { toast(errText(e), 'err') } finally { this.busy = '' }
    },
    async setDefault(c) {
      this.busy = 'def' + c.id
      try {
        const card = this.cloneDeep(c)
        card.status = 'published'
        await callData('rcbot.card.save', { card, set_default: true })
        toast('已设为默认角色', 'ok')
        await this.load()
      } catch (e) { toast(errText(e), 'err') } finally { this.busy = '' }
    },
    async cloneCard(c) {
      this.busy = 'clone' + c.id
      try {
        const r = await callData('rcbot.card.clone', { id: c.id })
        toast('已复制一份', 'ok')
        await this.load()
        if (r && r.id) this.pick(this.list.find((x) => x.id === r.id) || null)
      } catch (e) { toast(errText(e), 'err') } finally { this.busy = '' }
    },
    async del(c) {
      if (!confirm('删除角色卡片「' + (c.name || c.id) + '」？\n\n用到它的会话会回落到默认角色。')) return
      this.busy = 'del' + c.id
      try {
        await callData('rcbot.card.delete', { id: c.id })
        toast('已删除', 'ok')
        if (this.cur && this.cur.id === c.id) this.cur = null
        await this.load()
      } catch (e) { toast(errText(e), 'err') } finally { this.busy = '' }
    },
    async exportJson(c) {
      try {
        const d = await callData('rcbot.card.export', { id: c.id })
        const blob = new Blob([(d && d.json) || JSON.stringify(c, null, 2)], { type: 'application/json' })
        const a = document.createElement('a')
        a.href = URL.createObjectURL(blob)
        a.download = 'card-' + String(c.name || c.id).replace(/[^\w一-龥-]/g, '_') + '.json'
        a.click()
        setTimeout(() => URL.revokeObjectURL(a.href), 3000)
        toast('已导出卡片 JSON', 'ok')
      } catch (e) { toast(errText(e), 'err') }
    },
    importJson() {
      const inp = document.createElement('input')
      inp.type = 'file'
      inp.accept = 'application/json,.json'
      inp.onchange = async () => {
        const f = inp.files && inp.files[0]
        if (!f) return
        try {
          const text = await f.text()
          const r = await callData('rcbot.card.import', { json: text })
          toast('已导入：' + ((r && r.name) || '角色卡片'), 'ok')
          await this.load()
          if (r && r.id) this.pick(this.list.find((x) => x.id === r.id) || null)
        } catch (e) { toast(errText(e), 'err') }
      }
      inp.click()
    },
  },
  template: `
  <div class="rcq-split" :style="memoryOpen ? { gridTemplateColumns: '1fr' } : null">
    <!-- 左：卡片列表 -->
    <div class="rcq-pnl flat" v-if="!memoryOpen">
      <div class="rcq-ph" style="padding:14px 16px 0;margin-bottom:10px">
        <b>角色卡片</b><span class="sp"></span>
        <button class="btn btn-sm" @click="importJson">导入</button>
        <button class="btn btn-sm btn-primary" @click="add">新建</button>
      </div>
      <div class="rcq-list cd-grid">
        <div class="cd-card" v-for="c in list" :key="c.id"
          :class="{ on: cur && cur.id === c.id }" @click="pick(c)">
          <div class="cdc-cover" :style="coverStyle(c)">
            <span class="cdc-fallback" v-if="!assetSrc(c, 'cover')">{{ (c.name || '?').slice(0, 1) }}</span>
          </div>
          <img v-if="avatarSrc(c)" class="cdc-ava" :src="avatarSrc(c)" alt=""
            @error="$event.target.style.display='none'" />
          <div class="cdc-body">
            <div class="cdc-name">{{ c.name || '未命名' }}</div>
            <div class="cdc-tag">{{ c.tagline || (c.prompt || '').slice(0, 40) }}</div>
            <div class="cdc-badges">
              <span class="cd-tag" v-if="c.id === def">默认</span>
              <span class="cd-tag draft" v-if="c.status !== 'published'">草稿</span>
              <span class="cd-tag v">v{{ c.version || 1 }}</span>
            </div>
          </div>
        </div>
        <div v-if="!list.length" class="rcq-empty" style="grid-column:1/-1">
          <b>☺</b>还没有角色卡片，点「新建」加一个</div>
      </div>
    </div>

    <!-- 右：记忆星空 -->
    <div class="rcq-pnl" v-if="cur && memoryOpen">
      <div class="rcq-ph">
        <button class="btn btn-sm" @click="backToList">← 卡片</button>
        <b style="margin-left:8px">{{ cur.name || '角色' }} · 记忆</b><span class="sp"></span>
        <span class="rcq-hint" v-if="mem"> · {{ mem.total }} 颗星 · {{ (mem.main || []).length }} 主星 · 垃圾场 {{ mem.junk || 0 }}</span>
      </div>

      <!-- 卡片本体（已并入记忆，不再展示） -->
      <div class="cd-hero" v-if="false" :class="{ grad: !assetSrc(cur, 'cover') }">
        <div class="cdh-cover" :style="coverStyle(cur)"></div>
        <div class="cdh-inner">
          <div class="cdh-ava">
            <img v-if="assetSrc(cur, 'avatar')" :src="assetSrc(cur, 'avatar')" alt="" />
            <span v-else>{{ (cur.name || '?').slice(0, 1) }}</span>
          </div>
          <div class="cdh-title">
            <div class="cdh-name">{{ cur.name || '未命名' }}</div>
            <div class="cdh-alias" v-if="cur.alias && cur.alias.length">{{ cur.alias.join(' / ') }}</div>
            <div class="cdh-tag">{{ cur.tagline || '（还没有简介）' }}</div>
            <div class="cdh-badges">
              <span class="cd-tag" v-if="cur.id === def">默认角色</span>
              <span class="cd-tag draft" v-if="cur.status !== 'published'">草稿</span>
              <span class="cd-tag v">v{{ cur.version || 1 }}</span>
            </div>
          </div>
        </div>
        <div class="cdh-sections" v-if="(cur.greetings || []).length || (cur.examples || []).length || (cur.lorebook || []).length">
          <div class="cdh-sec" v-if="(cur.greetings || []).length">
            <b>开场白</b>
            <div class="cdh-line" v-for="(g, i) in cur.greetings" :key="'g' + i">「{{ g }}」</div>
          </div>
          <div class="cdh-sec" v-if="(cur.examples || []).length">
            <b>示例对话</b>
            <div class="cdh-ex" v-for="(ex, i) in cur.examples" :key="'e' + i">
              <div class="u">› {{ ex.user }}</div>
              <div class="a">{{ ex.assistant }}</div>
            </div>
          </div>
          <div class="cdh-sec" v-if="(cur.lorebook || []).length">
            <b>世界书</b>
            <div class="cdh-lore" v-for="(l, i) in cur.lorebook" :key="'l' + i">
              <span class="k">{{ (l.keys || []).join('、') }}</span>{{ l.content }}
            </div>
          </div>
        </div>
      </div>

      <div class="cd-tabs" v-if="false">
        <button :class="{ on: section === 'basic' }" @click="section = 'basic'">形象</button>
        <button :class="{ on: section === 'content' }" @click="section = 'content'">内容</button>
        <button :class="{ on: section === 'behavior' }" @click="section = 'behavior'">行为</button>
        <button :class="{ on: section === 'memory' }" @click="openSection('memory')">记忆</button>
      </div>

      <!-- 形象 -->
      <div class="rcq-form" v-if="false">
        <label class="rcq-fi wide"><span>名称</span>
          <input class="input" v-model="cur.name" @input="dirty = true" placeholder="例如：雨咯" />
        </label>
        <label class="rcq-fi wide"><span>一句话简介</span>
          <input class="input" v-model="cur.tagline" @input="dirty = true"
            placeholder="列表页显示的那句话" />
        </label>
        <label class="rcq-fi wide"><span>封面图</span>
          <input class="input" v-model="cur.cover" @input="dirty = true"
            placeholder="https://… 或 cards/<卡片ID>/cover.jpg" />
        </label>
        <label class="rcq-fi wide"><span>头像</span>
          <input class="input" v-model="cur.avatar" @input="dirty = true"
            placeholder="https://… 或 cards/<卡片ID>/avatar.png" />
        </label>
        <label class="rcq-fi wide"><span>立绘</span>
          <input class="input" v-model="cur.portrait" @input="dirty = true"
            placeholder="https://… 或 cards/<卡片ID>/portrait.png" />
        </label>
        <div class="rcq-hint wide" style="width:100%;margin:-4px 0 6px">
          填相对媒体目录的路径（如 cards/&lt;卡片ID&gt;/cover.jpg）＝ 图片由面板本机托管，永不失效；
          填 http(s) 外链则每次都去网上取。保存后可在上面预览。
        </div>
        <label class="rcq-fi"><span>状态</span>
          <select class="input" v-model="cur.status" @change="dirty = true">
            <option value="draft">草稿</option>
            <option value="published">已发布</option>
          </select>
        </label>
        <label class="rcq-fi"><span>版本</span>
          <input class="input" v-model.number="cur.version" @input="dirty = true" type="number" min="1" />
        </label>
      </div>

      <!-- 内容 -->
      <div class="rcq-form" v-if="false">
        <label class="rcq-fi wide"><span>系统提示词</span>
          <textarea class="rcq-ta tall" v-model="cur.prompt" @input="dirty = true"
            placeholder="描述它的身份、语气、边界。例如：你叫小雨，说话简短自然，不用敬语，不主动提自己是 AI。"></textarea>
        </label>

        <div class="cd-blk">
          <div class="cd-blk-h"><b>开场白</b>
            <button class="btn btn-sm" @click="addGreeting">添加一条</button></div>
          <div class="cd-item" v-for="(g, i) in cur.greetings" :key="'g' + i">
            <textarea class="rcq-ta" v-model="cur.greetings[i]" @input="dirty = true"
              placeholder="进入会话时随机说的一句话"></textarea>
            <button class="cd-x" title="删除" @click="rmGreeting(i)">×</button>
          </div>
          <div class="rcq-hint" v-if="!(cur.greetings || []).length">还没有开场白</div>
        </div>

        <div class="cd-blk">
          <div class="cd-blk-h"><b>示例对话</b>
            <button class="btn btn-sm" @click="addExample">添加一组</button></div>
          <div class="cd-item col" v-for="(ex, i) in cur.examples" :key="'e' + i">
            <div class="cd-row2">
              <input class="input" v-model="cur.examples[i].user" @input="dirty = true" placeholder="用户说" />
              <input class="input" v-model="cur.examples[i].assistant" @input="dirty = true" placeholder="角色回" />
              <button class="cd-x" title="删除" @click="rmExample(i)">×</button>
            </div>
          </div>
          <div class="rcq-hint" v-if="!(cur.examples || []).length">还没有示例</div>
        </div>

        <div class="cd-blk">
          <div class="cd-blk-h"><b>世界书</b>
            <button class="btn btn-sm" @click="addLore">添加一条</button></div>
          <div class="cd-item col" v-for="(l, i) in cur.lorebook" :key="'l' + i">
            <div class="cd-row2">
              <input class="input" :value="loreKeys(l)" @input="setLoreKeys(l, $event.target.value); dirty = true"
                placeholder="触发关键词（顿号分隔）" />
              <button class="cd-x" title="删除" @click="rmLore(i)">×</button>
            </div>
            <textarea class="rcq-ta" v-model="cur.lorebook[i].content" @input="dirty = true"
              placeholder="这条背景设定"></textarea>
          </div>
          <div class="rcq-hint" v-if="!(cur.lorebook || []).length">还没有世界书条目</div>
        </div>

        <label class="rcq-fi wide"><span>禁则（每行一条）</span>
          <textarea class="rcq-ta" :value="taboosText()" @input="setTaboosText($event.target.value); dirty = true"
            placeholder="不要说的话、 不要做的事"></textarea>
        </label>
      </div>

      <!-- 行为 -->
      <div class="rcq-form" v-if="false">
        <label class="rcq-fi wide"><span>模型提供商</span>
          <select class="input" v-model="cur.model.provider_id" @change="dirty = true">
            <option value="">（跟随账号默认）</option>
            <option v-for="p in providers" :key="p.id" :value="p.id">{{ p.name || p.id }}</option>
          </select>
        </label>
        <label class="rcq-fi wide"><span>模型名</span>
          <input class="input" v-model="cur.model.model" @input="dirty = true" placeholder="留空 = 用提供商的默认模型" />
        </label>
        <label class="rcq-fi"><span>温度</span>
          <input class="input" type="number" step="0.1" min="0" max="2"
            v-model.number="cur.style.temperature" @input="dirty = true" />
        </label>
        <label class="rcq-fi"><span>最大 tokens</span>
          <input class="input" type="number" step="64" min="64"
            v-model.number="cur.style.max_tokens" @input="dirty = true" />
        </label>
        <label class="rcq-fi"><span>最多字数</span>
          <input class="input" type="number" step="10" min="0" placeholder="不限"
            v-model.number="cur.style.max_chars" @input="dirty = true" />
        </label>
        <label class="rcq-fi"><span>允许 emoji</span>
          <label class="switch">
            <input type="checkbox" :checked="!!cur.style.allow_emoji"
              @change="cur.style.allow_emoji = $event.target.checked; dirty = true" />
            <span class="slider"></span>
          </label>
        </label>
        <label class="rcq-fi"><span>上下文轮数</span>
          <input class="input" type="number" min="1"
            v-model.number="cur.context.keep_rounds" @input="dirty = true" />
        </label>
            <label class="rcq-fi"><span>气泡色</span>
          <input class="input" v-model="cur.style.color" @input="dirty = true" placeholder="#12b7f5" />
        </label>
        <label class="rcq-fi"><span>回复方式</span>
          <select class="input" v-model="cur.style.reply_mode" @change="dirty = true">
            <option value="auto">自动（长了拆多条）</option>
            <option value="single">总是单条</option>
            <option value="multi">尽量多条短句</option>
          </select>
        </label>
        <label class="rcq-fi"><span>每条最多字数</span>
          <input class="input" type="number" min="8" max="200"
            v-model.number="cur.style.part_chars" @input="dirty = true" />
        </label>
        <label class="rcq-fi"><span>最多几条</span>
          <input class="input" type="number" min="1" max="10"
            v-model.number="cur.style.max_parts" @input="dirty = true" />
        </label>
        <label class="rcq-fi"><span>发送间隔（秒）</span>
          <input class="input" type="number" step="0.05" min="0" max="2"
            v-model.number="cur.style.part_delay" @input="dirty = true" />
        </label>
      </div>

      <div class="rcq-sec" v-if="false">
        <div class="rcq-ph" style="margin-bottom:8px"><b>关键词必回</b>
          <span class="rcq-hint">命中关键词直接回固定文案，不调模型、不受 AI 开关影响</span></div>
        <div v-for="(k, i) in (cur.keywords || [])" :key="i" class="rcq-flex"
          style="gap:8px;margin-bottom:8px;flex-wrap:wrap">
          <input class="input" style="flex:1;min-width:130px" v-model="k.match"
            placeholder="关键词" @input="dirty = true" />
          <input class="input" style="flex:2;min-width:200px" v-model="k.reply"
            placeholder="回复内容，支持 {nick}" @input="dirty = true" />
          <select class="input" style="width:110px" v-model="k.mode" @change="dirty = true">
            <option value="contains">包含</option>
            <option value="exact">完全匹配</option>
          </select>
          <label class="rcq-hint"><input type="checkbox" v-model="k.require_at"
            @change="dirty = true" /> 需 @</label>
          <label class="rcq-hint"><input type="checkbox" v-model="k.enabled"
            @change="dirty = true" /> 启用</label>
          <button class="btn btn-sm" @click="rmKw(i)">删除</button>
        </div>
        <button class="btn btn-sm" @click="addKw">+ 添加关键词</button>
        <div class="rcq-note" v-if="!(cur.keywords || []).length">
          例如「打卡」→「打卡成功，今天也要加油」；群里默认需要 @ 机器人，私聊不需要。
        </div>
      </div>

      <div class="rcq-sec" v-if="section === 'memory'" style="position:relative">
        <div class="rcq-flex" style="justify-content:space-between;align-items:center;margin-bottom:8px">
          <div><b>记忆星空</b>
            <span class="rcq-hint" v-if="mem"> · {{ mem.total }} 颗星 · {{ (mem.main || []).length }} 主星 · 垃圾场 {{ mem.junk || 0 }}</span>
            <span class="rcq-hint" v-else-if="memLoading">星域加载中…</span>
          </div>
          <div class="rcq-flex" style="gap:6px">
            <select class="input" style="width:190px" v-model="memScopeKey" @change="changeScope">
              <option value="global">全局记忆</option>
              <optgroup label="群聊" v-if="memScopes.groups.length">
                <option v-for="g in memScopes.groups" :key="g.key" :value="g.key">{{ g.label }}</option>
              </optgroup>
              <optgroup label="私聊" v-if="memScopes.privates.length">
                <option v-for="p in memScopes.privates" :key="p.key" :value="p.key">{{ p.label }}</option>
              </optgroup>
            </select>
            <input class="input" style="width:170px" v-model="memQuery" @input="searchMem"
              @keyup.enter="openFirstHit" @keyup.esc="clearSearch" placeholder="搜索记忆…" />
            <button v-if="memQuery" class="btn btn-sm" @click="clearSearch">×</button>
            <span class="rcq-hint" v-if="memQuery">{{ memHits.length }} 条</span>
            <button v-if="memHits.length" class="btn btn-sm" @click="openHit(-1)">‹</button>
            <button v-if="memHits.length" class="btn btn-sm" @click="openHit(1)">›</button>
            <button class="btn btn-sm" @click="toggleStats">统计</button>
            <button class="btn btn-sm" @click="consolidateMem">巩固</button>
            <button class="btn btn-sm" @click="openKeywords">关键词</button>
            <label class="rcq-hint"><input type="checkbox" v-model="showJunk"
              @change="toggleJunk" /> 显示垃圾场</label>
            <button class="btn btn-sm" @click="loadMemory">刷新</button>
            <button class="btn btn-sm" @click="fitMem">适配</button>
          </div>
        </div>
        <canvas ref="memCanvas" @mousedown="memDown" @mousemove="memMove" @mouseup="memUp"
          @mouseleave="memUp" @click="memClick" @wheel="memWheel"
          style="width:100%;height:calc(100vh - 210px);min-height:560px;border-radius:12px;display:block;cursor:grab;background:#05080f;border:1px solid rgba(120,160,220,.18)"></canvas>
        <div class="rcq-hint" style="margin-top:6px">拖动平移 · 滚轮缩放 · 点击星星查看 · 暗星会沉入垃圾场</div>
        <div v-if="showKeywords" style="position:absolute;inset:0;background:#070c14;z-index:30;border-radius:12px;padding:14px;overflow:auto;border:1px solid rgba(120,160,220,.25)">
          <div class="rcq-flex" style="justify-content:space-between;align-items:center;gap:8px;margin-bottom:10px">
            <b style="color:#f0f6ff">关键词管理 · {{ kwList.length }} 条</b>
            <span class="rcq-hint" style="color:#e6b85c">包含匹配 · 仅对已启用的群生效</span>
            <div class="rcq-flex" style="gap:6px;align-items:center">
              <input class="input" style="width:160px" v-model="kwQuery" placeholder="搜索关键词/回复…" />
              <span class="rcq-hint" style="color:#9fb2c8">{{ kwFiltered().length }} 条</span>
              <button class="btn btn-sm" @click="bulkKw(true)">全部启用</button>
              <button class="btn btn-sm" @click="bulkKw(false)">全部停用</button>
              <button class="btn btn-sm" @click="showKeywords = false">关闭</button>
            </div>
          </div>
          <div class="rcq-flex" style="gap:6px;margin-bottom:10px;flex-wrap:wrap;padding:8px;border:1px solid rgba(120,160,220,.2);border-radius:8px">
            <input class="input" style="width:150px" v-model="kwNew.match" placeholder="新关键词" />
            <input class="input" style="flex:1;min-width:200px" v-model="kwNew.reply" placeholder="兜底回复（模型失败时用）" />
            <span style="width:100px">包含匹配</span>
            <button class="btn btn-sm" @click="addKeyword">添加</button>
          </div>
          <div class="rcq-flex" style="font-size:11px;color:#8fa4bd;padding:0 4px 6px;gap:6px">
            <span style="width:150px">关键词</span><span style="flex:1">兜底回复（模型失败时用）</span>
            <span style="width:100px">匹配</span>
            <span style="width:44px">启用</span><span style="width:90px">操作</span>
          </div>
          <div v-for="k in kwFiltered().slice(0, kwLimit)" :key="k.id"
            class="rcq-flex" style="gap:6px;align-items:center;padding:4px 0;border-top:1px solid rgba(120,160,220,.08)">
            <input class="input" style="width:150px" v-model="k.match" @change="saveKw(k)" />
            <input class="input" style="flex:1;min-width:160px" v-model="k.reply" @change="saveKw(k)" />
            <span style="width:100px;color:#9fb2c8">包含</span>
            <input type="checkbox" style="width:44px" v-model="k.enabled" @change="saveKw(k)" />
            <button class="btn btn-sm" style="width:90px;color:#f5534f" @click="delKw(k)">删除</button>
          </div>
          <div v-if="kwFiltered().length > kwLimit" style="text-align:center;margin-top:10px">
            <button class="btn btn-sm" @click="kwLimit += 100">加载更多（剩余 {{ kwFiltered().length - kwLimit }}）</button>
          </div>
        </div>
        <div v-if="showStats && memStats" style="position:absolute;left:12px;top:44px;width:280px;max-height:470px;overflow:auto;background:rgba(10,16,26,.97);border:1px solid rgba(130,170,230,.4);border-radius:10px;padding:12px;box-shadow:0 8px 30px rgba(0,0,0,.6);color:#dbe7f5">
          <div class="rcq-flex" style="justify-content:space-between;align-items:center">
            <b style="color:#f0f6ff">记忆统计</b>
            <button class="btn btn-sm" @click="showStats = false">×</button>
          </div>
          <div class="rcq-hint" style="margin:8px 0;color:#9fb2c8">
            共 {{ memStats.total }} 条 · {{ memStats.chars }} 字 · 近 7 天 +{{ memStats.recent7d }}
          </div>
          <div v-for="(c, t) in memStats.types" :key="t" class="rcq-flex"
            style="justify-content:space-between;font-size:12px;padding:3px 0;color:#dbe7f5">
            <span>{{ memName(t) }}</span><b>{{ c }}</b>
          </div>
          <div class="rcq-hint" style="margin-top:8px;color:#9fb2c8">
            状态：正常 {{ (memStats.states && memStats.states.active) || 0 }} ·
            休眠 {{ (memStats.states && memStats.states.dormant) || 0 }} ·
            垃圾场 {{ (memStats.states && memStats.states.junk) || 0 }}
          </div>
          <div class="rcq-hint" style="color:#9fb2c8">
            范围：全局 {{ (memStats.scopes && memStats.scopes.global) || 0 }} ·
            群 {{ (memStats.scopes && memStats.scopes.group) || 0 }} ·
            私聊 {{ (memStats.scopes && memStats.scopes.private) || 0 }}
          </div>
        </div>
        <div v-if="memSel" style="position:absolute;right:10px;top:44px;width:330px;max-height:470px;overflow:auto;background:rgba(14,20,30,.96);border:1px solid rgba(120,160,220,.3);border-radius:10px;padding:12px;box-shadow:0 8px 30px rgba(0,0,0,.5)">
          <div class="rcq-flex" style="justify-content:space-between;align-items:center">
            <b>{{ memName(memSel.type) }}</b>
            <button class="btn btn-sm" @click="memSel = null">×</button>
          </div>
          <textarea class="input" v-model="memSel.content"
            style="width:100%;height:150px;margin:10px 0;font-size:13px;line-height:1.6;resize:vertical"></textarea>
          <div class="rcq-hint">重要度
            <input class="input" type="number" step="0.05" min="0" max="1"
              v-model.number="memSel.importance" style="width:70px;margin:0 6px" />
            · 使用 {{ memSel.use_count || 0 }} 次 · {{ memState(memSel.state) }}
          </div>
          <div class="rcq-flex" style="gap:8px;margin-top:10px">
            <button class="btn btn-sm" @click="saveMem">保存修改</button>
            <button class="btn btn-sm" @click="pinMem">{{ memSel.pinned ? '取消置顶' : '置顶' }}</button>
            <button class="btn btn-sm" @click="delMem">移入垃圾场</button>
          </div>
        </div>
      </div>

      <div class="rcq-flex" style="margin-top:12px" v-if="false">
        <button class="btn btn-sm" @click="setDefault(cur)">设为默认角色</button>
        <button class="btn btn-sm" style="color:var(--err,#f5534f)"
          :disabled="busy === 'del' + cur.id" @click="del(cur)">删除</button>
        <span class="rcq-hint" style="margin-left:auto">卡片 v{{ cur.version || 1 }} · {{ cur.status === 'published' ? '已发布' : '草稿' }}</span>
      </div>
      <div class="rcq-note" v-if="false">
        角色卡片是「定义」，账号和会话只引用它 —— 改卡片不会影响已经产生的历史会话。
        想给别的机器人用，直接「导出」成 JSON 发过去，对方「导入」即可。
      </div>
    </div>

    <div class="rcq-pnl" v-else>
      <div class="rcq-empty"><b>☺</b>左边选一张卡片，或者新建一张</div>
    </div>
  </div>`,
}

// ------------------------------------------------------------------ 会话管理

const Sessions = {
  data() {
    return {
      S, list: [], stats: {}, defPersona: '', defProvider: '',
      personas: [], providers: [], cur: null, detail: null, ctx: null,
      filter: 'all', kw: '', busy: '', err: '', limit: 60,
    }
  },
  computed: {
    shown() {
      const k = this.kw.trim().toLowerCase()
      return this.list.filter((s) => {
        if (this.filter === 'group' && s.kind !== 'group') return false
        if (this.filter === 'private' && s.kind === 'group') return false
        if (this.filter === 'off' && s.enabled !== 0) return false
        if (this.filter === 'on' && s.enabled === 0) return false
        if (!k) return true
        return ((s.display || '') + ' ' + (s.id || '') + ' ' + (s.target_id || '')).toLowerCase().indexOf(k) >= 0
      })
    },
    enabledCount() {
      return this.list.filter((s) => s.enabled !== 0).length
    },
    usedPct() {
      const c = this.ctx
      if (!c || !c.budget) return 0
      return Math.min(100, Math.round((c.est_tokens / c.budget) * 100))
    },
    barClass() { return this.usedPct >= 90 ? 'max' : (this.usedPct >= 70 ? 'hi' : '') },
  },
  async mounted() { await this.load() },
  methods: {
    fmtTime, fmtNum,
    async load() {
      this.busy = 'load'
      try {
        const d = await callData('rcbot.sessions')
        this.list = (d && d.items) || []
        this.stats = (d && d.stats) || {}
        this.defPersona = (d && d.default_persona) || ''
        this.defProvider = (d && d.default_provider) || ''
        const p = await callData('rcbot.personas')
        this.personas = (p && p.items) || []
        const pr = await callData('rcbot.providers')
        this.providers = (pr && pr.items) || []
        if (this.cur) {
          const same = this.list.find((x) => x.id === this.cur.id)
          if (same) this.cur = same
        }
      } catch (e) { this.err = errText(e) } finally { this.busy = '' }
    },
    async open(s) {
      this.cur = s
      this.busy = 'open'
      try {
        this.detail = await callData('rcbot.session.get', { id: s.id, limit: this.limit })
        this.ctx = await callData('rcbot.context', { id: s.id })
      } catch (e) { toast(errText(e), 'err') } finally { this.busy = '' }
    },
    // 拉取账号的全部群聊与好友，登记成会话目录
    // 新登记的一律默认「不启用」—— 机器人不会在没说过话的地方主动开口。
    async syncCatalog() {
      if (!confirm('从 QQ 拉取全部群聊与好友？\n\n拉到的会话默认都是「不启用」，需要你自己打开开关。')) return
      this.busy = 'sync'
      try {
        const r = await callData('rcbot.session.catalog', {})
        toast('已拉取：群 ' + (r.groups || 0) + ' 个、好友 ' + (r.friends || 0) +
              ' 个，新增会话 ' + (r.new || 0) + ' 个', 'ok')
        await this.load()
      } catch (e) { toast(errText(e), 'err') } finally { this.busy = '' }
    },
    async toggle(s, on) {
      const old = s.enabled
      s.enabled = on ? 1 : 0
      try {
        await call('rcbot.session.save', { id: s.id, enabled: on ? 1 : 0 })
      } catch (e) {
        s.enabled = old
        toast(errText(e), 'err')
      }
    },
    async bulk(on) {
      if (on && !confirm('启用全部会话？\n\n机器人会在这些群里自动回复（群里仍需 @ 或唤醒前缀）。')) return
      if (!on && !confirm('停用全部会话？机器人将不再自动回复。')) return
      this.busy = 'bulk'
      try {
        const r = await callData('rcbot.session.bulk', { enabled: on ? 1 : 0 })
        toast((on ? '已启用 ' : '已停用 ') + (r.changed || 0) + ' 个会话', 'ok')
        await this.load()
      } catch (e) { toast(errText(e), 'err') } finally { this.busy = '' }
    },
    async reloadDetail() {
      if (!this.cur) return
      try {
        this.detail = await callData('rcbot.session.get', { id: this.cur.id, limit: this.limit })
        this.ctx = await callData('rcbot.context', { id: this.cur.id })
      } catch (e) { toast(errText(e), 'err') }
    },
    async patch(field, value) {
      if (!this.cur) return
      this.busy = 'p' + field
      try {
        const body = { id: this.cur.id }
        body[field] = value
        await call('rcbot.session.save', body)
        toast('已更新', 'ok')
        await this.load()
        await this.reloadDetail()
      } catch (e) { toast(errText(e), 'err') } finally { this.busy = '' }
    },
    async clear() {
      if (!this.cur) return
      if (!confirm('清空「' + (this.cur.display || this.cur.id) + '」的上下文？消息会删掉，会话保留。')) return
      this.busy = 'clear'
      try {
        await call('rcbot.session.clear', { id: this.cur.id })
        toast('上下文已清空', 'ok')
        await this.load(); await this.reloadDetail()
      } catch (e) { toast(errText(e), 'err') } finally { this.busy = '' }
    },
    async del() {
      if (!this.cur) return
      if (!confirm('删除会话「' + (this.cur.display || this.cur.id) + '」？消息和摘要一起删。')) return
      this.busy = 'del'
      try {
        await call('rcbot.session.delete', { id: this.cur.id })
        toast('已删除', 'ok')
        this.cur = null; this.detail = null; this.ctx = null
        await this.load()
      } catch (e) { toast(errText(e), 'err') } finally { this.busy = '' }
    },
    personaName(id) {
      if (!id) return '默认'
      const p = this.personas.find((x) => x.id === id)
      return p ? p.name : id
    },
    providerName(id) {
      if (!id) return '默认'
      const p = this.providers.find((x) => x.id === id)
      return p ? (p.label || p.id) : id
    },
  },
  template: `
  <div>
    <div v-if="err" class="rcq-pnl rcq-warn" style="font-size:12px">{{ err }}</div>

    <div class="rcq-split">
      <div class="rcq-pnl flat">
        <div class="rcq-ph" style="padding:14px 16px 0;margin-bottom:10px">
          <b>会话</b>
          <span class="rcq-hint">{{ stats.sessions || 0 }} 个 · 消息 {{ fmtNum(stats.messages || 0) }}</span>
          <span class="sp"></span>
          <button class="btn btn-sm" :disabled="!!busy" @click="syncCatalog">
            {{ busy === 'sync' ? '拉取中…' : '拉取群聊/私聊' }}</button>
          <button class="btn btn-sm" :disabled="!!busy" @click="load">刷新</button>
        </div>
        <div class="rcq-flex" style="padding:0 16px 8px">
          <button class="btn btn-sm" :class="filter === 'all' ? 'btn-primary' : ''" @click="filter = 'all'">全部</button>
          <button class="btn btn-sm" :class="filter === 'group' ? 'btn-primary' : ''" @click="filter = 'group'">群聊</button>
          <button class="btn btn-sm" :class="filter === 'private' ? 'btn-primary' : ''" @click="filter = 'private'">私聊</button>
          <button class="btn btn-sm" :class="filter === 'on' ? 'btn-primary' : ''" @click="filter = 'on'">已启用</button>
          <button class="btn btn-sm" :class="filter === 'off' ? 'btn-primary' : ''" @click="filter = 'off'">已停用</button>
          <input class="input" style="flex:1;min-width:90px;padding:4px 10px;font-size:12px"
            v-model="kw" placeholder="搜会话" />
        </div>
        <div class="rcq-flex" style="padding:0 16px 8px;font-size:11.5px;color:var(--m)">
          <span>已启用 <b>{{ enabledCount }}</b> / {{ list.length }}</span>
          <span class="sp"></span>
          <button class="btn btn-sm" :disabled="!!busy" @click="bulk(true)">全部启用</button>
          <button class="btn btn-sm" :disabled="!!busy" @click="bulk(false)">全部停用</button>
        </div>
        <div class="rcq-list">
          <div class="rcq-row click" v-for="s in shown" :key="s.id"
            :class="{ on: cur && cur.id === s.id }" @click="open(s)">
            <div class="main">
              <div class="t">
                <span class="tag-chip tag-chip-sm">{{ s.kind === 'group' ? '群' : '私' }}</span>
                {{ s.display || s.target_id || s.id }}
                <span class="tag-chip tag-chip-sm" v-if="!s.talked">未聊过</span>
                <span class="tag-chip tag-chip-sm" v-if="s.enabled === 0">已停用</span>
              </div>
              <div class="d">
                {{ s.msg_count || 0 }} 条 · {{ s.mode_label || '' }}
                <template v-if="s.persona_id"> · {{ personaName(s.persona_id) }}</template>
                · {{ fmtTime(s.last_at || s.updated_at) }}
              </div>
            </div>
            <div class="acts" @click.stop>
              <label class="switch" :title="s.enabled === 0 ? '启用这个会话' : '停用这个会话'">
                <input type="checkbox" :checked="s.enabled !== 0" :disabled="!!busy"
                  @change="toggle(s, $event.target.checked)" />
                <span class="slider"></span>
              </label>
            </div>
          </div>
          <div v-if="!shown.length" class="rcq-empty"><b>▤</b>没有会话</div>
        </div>
      </div>

      <div v-if="cur">
        <div class="rcq-pnl">
          <div class="rcq-ph">
            <b>{{ cur.display || cur.target_id }}</b>
            <span class="tag-chip tag-chip-sm">{{ cur.kind === 'group' ? '群聊' : '私聊' }}</span>
            <span class="tag-chip tag-chip-sm">{{ cur.mode_label || '' }}</span>
            <span class="sp"></span>
            <button class="btn btn-sm" :disabled="!!busy" @click="reloadDetail">刷新</button>
          </div>

          <div class="rcq-form">
            <label class="rcq-fi"><span>角色卡片</span>
              <select class="select" :value="cur.persona_id || ''" :disabled="!!busy"
                @change="patch('persona_id', $event.target.value)">
                <option value="">跟随默认（{{ personaName(defPersona) }}）</option>
                <option v-for="p in personas" :key="p.id" :value="p.id">{{ p.name || p.id }}</option>
              </select>
            </label>
            <label class="rcq-fi"><span>模型提供商</span>
              <select class="select" :value="cur.provider_id || ''" :disabled="!!busy"
                @change="patch('provider_id', $event.target.value)">
                <option value="">跟随默认（{{ providerName(defProvider) }}）</option>
                <option v-for="p in providers" :key="p.id" :value="p.id">{{ p.label || p.id }}</option>
              </select>
            </label>
            <div class="rcq-fi"><span>启用</span>
              <label class="switch">
                <input type="checkbox" :checked="cur.enabled !== 0" :disabled="!!busy"
                  @change="patch('enabled', $event.target.checked)" />
                <span class="slider"></span>
              </label>
            </div>
          </div>

          <div class="rcq-sec" v-if="ctx">
            <div class="rcq-flex" style="margin-bottom:4px">
              <span class="rcq-hint">上下文占用</span>
              <span class="sp" style="margin-left:auto"></span>
              <span class="rcq-mono">{{ ctx.est_tokens }} / {{ ctx.budget }} tokens（{{ usedPct }}%）</span>
            </div>
            <div class="rcq-bar2"><i :class="barClass" :style="{ width: usedPct + '%' }"></i></div>
            <div class="rcq-note">
              预算 = 上下文窗口 − 最大输出 − 系统提示。超了就按「保留最近比例」压缩成摘要。
            </div>
            <div class="rcq-flex" style="margin-top:10px">
              <button class="btn btn-sm" :disabled="!!busy" @click="clear">清空上下文</button>
              <button class="btn btn-sm btn-danger" :disabled="!!busy" @click="del">删除会话</button>
            </div>
          </div>
        </div>

        <div class="rcq-pnl" v-if="detail">
          <div class="rcq-ph"><b>消息记录</b><span class="sp"></span>
            <span class="rcq-hint">最近 {{ (detail.messages || []).length }} / 共 {{ detail.msg_count || 0 }} 条</span></div>

          <div v-if="detail.summary" class="rcq-pnl" style="background:var(--sf2);margin-bottom:12px">
            <div class="rcq-ph" style="margin-bottom:6px"><b>压缩摘要</b>
              <span class="rcq-hint">旧对话被压成了这段</span></div>
            <div style="font-size:12.5px;white-space:pre-wrap">{{ detail.summary }}</div>
          </div>

          <div class="rcq-msgs">
            <div class="rcq-msg" v-for="m in (detail.messages || [])" :key="m.id"
              :class="{ me: m.role === 'assistant' }">
              <div class="who">{{ m.role === 'assistant' ? '助手' : (m.name || '用户') }}</div>
              <div class="body">{{ m.content }}</div>
            </div>
            <div v-if="!(detail.messages || []).length" class="rcq-empty"><b>▤</b>这个会话还没有消息</div>
          </div>
        </div>
      </div>

      <div class="rcq-pnl" v-else>
        <div class="rcq-empty"><b>▤</b>左边点一个会话看详情</div>
      </div>
    </div>
  </div>`,
}

// ------------------------------------------------------------------ 模型提供商

const Providers = {
  data() {
    return {
      S, list: [], def: '', cur: null, busy: '', err: '', dirty: false,
      test: null, models: [], showKey: false,
    }
  },
  computed: { isNew() { return !!(this.cur && this.cur.__new) } },
  async mounted() { await this.load() },
  methods: {
    async load() {
      try {
        const d = await callData('rcbot.providers')
        this.list = (d && d.items) || []
        this.def = (d && d.default) || ''
        if (!this.cur) this.pick(this.list[0] || null)
        else if (!this.cur.__new && !this.dirty) {
          const same = this.list.find((x) => x.id === this.cur.id)
          if (same) this.pick(same)
        }
      } catch (e) { this.err = errText(e) }
    },
    pick(p) {
      this.cur = p ? Object.assign({ type: 'openai', timeout: 120, enable: true }, p) : null
      this.dirty = false; this.test = null; this.models = []
    },
    add() {
      this.cur = {
        id: '', label: '', type: 'openai', api_base: 'https://api.openai.com/v1',
        api_key: '', model: '', timeout: 120, enable: true, __new: true,
      }
      this.dirty = true; this.test = null; this.models = []
    },
    async save() {
      const c = this.cur
      if (!c) return
      if (!String(c.label || '').trim()) { toast('给提供商起个名字', 'err'); return }
      if (!String(c.api_base || '').trim()) { toast('api_base 不能为空', 'err'); return }
      this.busy = 'save'
      try {
        await call('rcbot.provider.save', {
          id: c.__new ? '' : c.id, label: c.label, type: c.type,
          api_base: c.api_base, api_key: c.api_key, model: c.model,
          timeout: Number(c.timeout) || 120, enable: !!c.enable,
        })
        toast('已保存', 'ok'); this.dirty = false
        this.cur = null
        await this.load()
      } catch (e) { toast(errText(e), 'err') } finally { this.busy = '' }
    },
    async setDefault(p) {
      this.busy = 'def' + p.id
      try {
        await call('rcbot.provider.save', {
          id: p.id, label: p.label, type: p.type, api_base: p.api_base,
          api_key: p.api_key, model: p.model, timeout: p.timeout, enable: p.enable,
          set_default: true,
        })
        toast('已设为默认提供商', 'ok')
        await this.load()
      } catch (e) { toast(errText(e), 'err') } finally { this.busy = '' }
    },
    async del(p) {
      if (!confirm('删除提供商「' + (p.label || p.id) + '」？')) return
      this.busy = 'del' + p.id
      try {
        await call('rcbot.provider.delete', { id: p.id })
        toast('已删除', 'ok'); this.cur = null
        await this.load()
      } catch (e) { toast(errText(e), 'err') } finally { this.busy = '' }
    },
    async doTest(p) {
      this.busy = 'test' + p.id
      this.test = null
      try {
        const r = await callData('rcbot.provider.test', { id: p.id })
        this.test = Object.assign({ id: p.id }, r || {})
        toast(r.ok ? ('通了，' + r.ms + 'ms') : ('不通：' + (r.error || '')), r.ok ? 'ok' : 'err')
      } catch (e) { toast(errText(e), 'err') } finally { this.busy = '' }
    },
    async fetchModels() {
      const c = this.cur
      if (!c || c.__new) { toast('先保存再拉模型列表', 'err'); return }
      this.busy = 'models'
      try {
        const r = await callData('rcbot.provider.models', { id: c.id })
        this.models = (r && (r.items || r.models)) || []
        if (!this.models.length) toast('没拉到模型', 'err')
      } catch (e) { toast(errText(e), 'err') } finally { this.busy = '' }
    },
  },
  template: `
  <div class="rcq-split">
    <div class="rcq-pnl flat">
      <div class="rcq-ph" style="padding:14px 16px 0;margin-bottom:10px">
        <b>模型提供商</b><span class="sp"></span>
        <button class="btn btn-sm btn-primary" @click="add">新增</button>
      </div>
      <div class="rcq-list">
        <div class="rcq-row click" v-for="p in list" :key="p.id"
          :class="{ on: cur && cur.id === p.id }" @click="pick(p)">
          <div class="main">
            <div class="t">{{ p.label || p.id }}
              <span class="tag-chip tag-chip-sm" v-if="p.id === def">默认</span>
              <span class="tag-chip tag-chip-sm" v-if="p.enable === false">停用</span>
            </div>
            <div class="d">{{ p.model || '未选模型' }} · {{ p.api_base }}</div>
          </div>
        </div>
        <div v-if="!list.length" class="rcq-empty"><b>✦</b>还没有提供商，点「新增」</div>
      </div>
    </div>

    <div class="rcq-pnl" v-if="cur">
      <div class="rcq-ph"><b>{{ isNew ? '新增提供商' : (cur.label || cur.id) }}</b><span class="sp"></span>
        <span class="tag-chip tag-chip-sm" v-if="cur.id && cur.id === def">默认</span>
      </div>
      <div class="rcq-form">
        <label class="rcq-fi"><span>名称</span>
          <input class="input" v-model="cur.label" @input="dirty = true" placeholder="DeepSeek" /></label>
        <label class="rcq-fi"><span>协议</span>
          <select class="select" v-model="cur.type" @change="dirty = true">
            <option value="openai">OpenAI 兼容</option>
            <option value="anthropic">Anthropic</option>
          </select></label>
        <label class="rcq-fi wide"><span>API 地址</span>
          <input class="input" v-model="cur.api_base" @input="dirty = true"
            placeholder="https://api.deepseek.com/v1" /></label>
        <label class="rcq-fi wide"><span>API Key</span>
          <div style="display:flex;gap:6px">
            <input class="input" style="flex:1" v-model="cur.api_key" @input="dirty = true"
              :type="showKey ? 'text' : 'password'" placeholder="sk-..." />
            <button class="btn btn-sm" @click="showKey = !showKey">{{ showKey ? '隐藏' : '显示' }}</button>
          </div>
        </label>
        <label class="rcq-fi"><span>模型</span>
          <div style="display:flex;gap:6px">
            <input class="input" style="flex:1" v-model="cur.model" @input="dirty = true"
              placeholder="deepseek-flash" />
            <button class="btn btn-sm" :disabled="!!busy || isNew" @click="fetchModels">拉列表</button>
          </div>
        </label>
        <label class="rcq-fi"><span>超时（秒）</span>
          <input class="input" type="number" min="10" max="600" v-model="cur.timeout" @input="dirty = true" /></label>
        <div class="rcq-fi" v-if="models.length"><span>从列表选（{{ models.length }}）</span>
          <select class="select" :value="cur.model" @change="cur.model = $event.target.value; dirty = true">
            <option v-for="m in models" :key="m" :value="m">{{ m }}</option>
          </select>
        </div>
      </div>

      <div class="rcq-flex" style="margin-top:12px">
        <button class="btn btn-primary btn-sm" :disabled="!!busy" @click="save">保存</button>
        <button class="btn btn-sm" v-if="cur.id && cur.id !== def" :disabled="!!busy"
          @click="setDefault(cur)">设为默认</button>
        <button class="btn btn-sm" v-if="cur.id && !isNew" :disabled="!!busy" @click="doTest(cur)">测试连通</button>
        <button class="btn btn-sm btn-danger" v-if="cur.id && !isNew" :disabled="!!busy"
          @click="del(cur)">删除</button>
        <span class="rcq-hint" v-if="dirty">有未保存的修改</span>
      </div>
      <div class="rcq-note" v-if="test">
        <span :style="{ color: test.ok ? 'var(--success)' : 'var(--danger)' }">
          {{ test.ok ? ('连通 ' + test.ms + 'ms · 回复：' + (test.reply || '')) : ('失败：' + (test.error || '')) }}
        </span>
      </div>
      <div class="rcq-note">
        推理模型（deepseek-flash 等）会先花 token 在思考上，测连通至少给 256 个输出 token，
        所以「测试连通」偶尔慢一点是正常的。
      </div>
    </div>

    <div class="rcq-pnl" v-else>
      <div class="rcq-empty"><b>✦</b>左边选一个，或者新增</div>
    </div>
  </div>`,
}

// ------------------------------------------------------------------ 运行日志（SnowLuma 容器）

const Logs = {
  data() {
    return {
      S, items: [], mode: 'live', level: '', lines: 400, follow: true,
      source: '', connected: false, hint: '', busy: false, timer: null, err: '',
      stats: null,
    }
  },
  computed: {
    filtered() { return this.items },
  },
  async mounted() { await this.load(); await this.loadStats(); this.tick() },
  beforeUnmount() { if (this.timer) clearTimeout(this.timer) },
  methods: {
    tick() {
      if (this.timer) clearTimeout(this.timer)
      if (this.mode === 'live' && this.follow) {
        this.timer = setTimeout(async () => {
          await this.load(true)
          await this.loadStats(true)
          this.tick()
        }, 2000)
      }
    },
    async loadStats(silent) {
      try {
        this.stats = await callData('qqbot.tools.stats', {})
      } catch (e) { if (!silent) this.err = errText(e) }
    },
    async load(silent) {
      if (!silent) this.busy = true
      try {
        const d = await call('qqbot.account.logs', {
          mode: this.mode, level: this.level, lines: Number(this.lines) || 400,
        })
        const grow = d.items.length !== this.items.length
        this.items = d.items || []
        this.source = d.source
        this.connected = !!d.connected
        this.hint = d.hint || ''
        this.err = ''
        if (grow && this.follow) this.$nextTick(this.scrollBottom)
      } catch (e) {
        this.err = errText(e)
      } finally {
        this.busy = false
      }
    },
    scrollBottom() {
      const el = this.$refs.box
      if (el) el.scrollTop = el.scrollHeight
    },
    async switchMode(m) {
      this.mode = m
      this.items = []
      await this.load()
      this.tick()
    },
    async setLevel(l) {
      this.level = this.level === l ? '' : l
      await this.load()
    },
    async clear() {
      try {
        await call('qqbot.account.logs.clear')
        this.items = []
        toast('已清空当前视图（容器日志由 Docker 管理）', 'ok')
      } catch (e) { toast(errText(e), 'err') }
    },
    download() {
      const txt = this.items.map((x) => '[' + String(x.level).toUpperCase() + '] ' + x.text).join('\n')
      const blob = new Blob([txt], { type: 'text/plain;charset=utf-8' })
      const a = document.createElement('a')
      a.href = URL.createObjectURL(blob)
      a.download = 'snowluma-' + Date.now() + '.log'
      a.click()
      setTimeout(() => URL.revokeObjectURL(a.href), 3000)
    },
    lineClass(x) { return 'rcq-ln rcq-lv-' + (x.level || 'info') },
    lvText(x) { return '[' + String(x.level || 'info').toUpperCase() + ']' },
  },
  template: `
  <div>
    <div class="rcq-pnl">
      <div class="rcq-ph">
        <button class="btn btn-sm" :class="mode === 'live' ? 'btn-primary' : ''" @click="switchMode('live')">实时日志</button>
        <button class="btn btn-sm" :class="mode === 'history' ? 'btn-primary' : ''" @click="switchMode('history')">历史日志</button>
        <span class="sp"></span>
        <span class="rcq-lamp"><b :class="connected ? 'on' : 'off'"></b>
          {{ connected ? '容器在线' : '容器离线' }} · docker logs</span>
      </div>
      <div class="rcq-flex">
        <span class="rcq-hint">日志级别</span>
        <button class="btn btn-sm" :class="level === 'debug' ? 'btn-primary' : ''" @click="setLevel('debug')">Debug</button>
        <button class="btn btn-sm" :class="level === 'info' ? 'btn-primary' : ''" @click="setLevel('info')">Info</button>
        <button class="btn btn-sm" :class="level === 'warn' ? 'btn-primary' : ''" @click="setLevel('warn')">Warn</button>
        <button class="btn btn-sm" :class="level === 'error' ? 'btn-primary' : ''" @click="setLevel('error')">Error</button>
        <span style="width:10px"></span>
        <select class="select" style="padding:4px 8px;font-size:12px" v-model.number="lines" @change="load()">
          <option :value="200">200 行</option>
          <option :value="400">400 行</option>
          <option :value="1000">1000 行</option>
          <option :value="2000">2000 行</option>
        </select>
        <label class="switch" title="自动跟随">
          <input type="checkbox" v-model="follow" @change="tick" />
          <span class="slider"></span>
        </label>
        <span class="rcq-hint">跟随</span>
        <span class="sp" style="margin-left:auto"></span>
        <button class="btn btn-sm" :disabled="busy" @click="load()">刷新</button>
        <button class="btn btn-sm" @click="download">下载</button>
        <button class="btn btn-sm" v-if="mode === 'live'" @click="clear">清空</button>
      </div>
    </div>

    <div class="rcq-pnl">
      <div class="rcq-flex">
        <b>工具调用统计</b>
        <span class="rcq-hint">本次进程运行以来（AI 调用 + 手动测试）</span>
        <span style="margin-left:auto"></span>
        <button class="btn btn-sm" @click="loadStats()">刷新</button>
      </div>
      <div v-if="stats" class="rcq-flex" style="gap:18px;margin-top:8px;flex-wrap:wrap">
        <span class="rcq-hint">总调用 <b>{{ stats.total }}</b></span>
        <span class="rcq-hint">成功 <b style="color:var(--ok,#5fd38d)">{{ stats.ok }}</b></span>
        <span class="rcq-hint">失败 <b style="color:var(--bad,#e0533f)">{{ stats.fail }}</b></span>
        <span class="rcq-hint">成功率 <b>{{ stats.rate }}%</b></span>
      </div>
      <div v-if="stats && stats.tools.length" style="margin-top:8px">
        <div v-for="t in stats.tools" :key="t.id" class="rcq-flex"
          style="padding:7px 0;border-bottom:1px solid var(--bd)">
          <b style="min-width:110px">{{ t.name }}</b>
          <span class="rcq-hint">调用 {{ t.calls }}</span>
          <span class="rcq-hint" style="margin-left:10px">成功 {{ t.ok }}</span>
          <span class="rcq-hint" style="margin-left:10px">失败 {{ t.fail }}</span>
          <span class="rcq-hint" style="margin-left:auto">平均 {{ t.avg_ms }}ms</span>
        </div>
      </div>
      <div v-else class="rcq-hint" style="margin-top:8px">还没有工具调用</div>
      <div v-if="stats && stats.recent.length" style="margin-top:10px">
        <div class="rcq-hint" style="margin-bottom:4px">最近调用</div>
        <div v-for="(r, i) in stats.recent" :key="i" class="rcq-flex"
          style="font-size:12px;padding:3px 0;border-bottom:1px dashed var(--bd)">
          <span class="mono" style="color:var(--m)">{{ r.time }}</span>
          <span style="margin-left:8px">{{ r.name }}</span>
          <span class="rcq-hint" style="margin-left:8px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:320px">{{ r.args }}</span>
          <span :style="{ marginLeft: 'auto', color: r.ok ? 'var(--ok,#5fd38d)' : 'var(--bad,#e0533f)' }">
            {{ r.ok ? 'ok' : 'fail' }} · {{ r.ms }}ms</span>
        </div>
      </div>
    </div>

    <div v-if="err" class="rcq-pnl rcq-warn" style="font-size:12px">{{ err }}</div>

    <div class="rcq-log" ref="box">
      <div v-for="(x, i) in items" :key="i" :class="lineClass(x)">
        <span class="lv">{{ lvText(x) }}</span>{{ x.text }}
      </div>
      <div v-if="!items.length" style="color:var(--f)">
        {{ hint || '还没有日志' }}
      </div>
    </div>
    <div class="rcq-note">
      日志来自 <code>docker logs snowluma</code>（容器日志本身带历史，每 2 秒刷新一次）。
      容器没起来时这里会是空的。
    </div>
  </div>`,
}

// ------------------------------------------------------------------ 设置

const Settings = {
  data() {
    return {
      S, cfg: null, conn: null, busy: '', err: '', searchQ: '', searchOut: null,
      tab: 'ctx',
    }
  },
  computed: {
    ctx() { return (this.cfg && this.cfg.context) || {} },
    bot() { return (this.cfg && this.cfg.bot) || {} },
    feats() { return (this.cfg && this.cfg.features) || {} },
    ws() { return this.feats.web_search || {} },
    vis() { return this.feats.vision || {} },
    rp() { return this.feats.random_pick || {} },
    sl() { return this.feats.sl_status || {} },
    ai() {
      if (!this.cfg) return { enabled: true }
      this.cfg.features = this.cfg.features || {}
      this.cfg.features.ai = this.cfg.features.ai || { enabled: true }
      return this.cfg.features.ai
    },
    pnl() {
      if (!this.cfg) return { enabled: true }
      this.cfg.features = this.cfg.features || {}
      this.cfg.features.panel = this.cfg.features.panel || { enabled: true }
      return this.cfg.features.panel
    },
  },
  async mounted() { await this.load() },
  methods: {
    async load() {
      this.busy = 'load'
      try {
        this.cfg = await callData('rcbot.config.get')
        this.conn = await call('qqbot.conn.get')
        this.err = ''
      } catch (e) { this.err = errText(e) } finally { this.busy = '' }
    },
    async saveCtx() {
      this.busy = 'ctx'
      try {
        await call('rcbot.config.save', {
          context: {
            max_tokens: Number(this.ctx.max_tokens) || 128000,
            max_output_tokens: Number(this.ctx.max_output_tokens) || 4096,
            keep_recent_ratio: Number(this.ctx.keep_recent_ratio) || 0.15,
            max_history_messages: Number(this.ctx.max_history_messages) || 200,
            compress_enabled: !!this.ctx.compress_enabled,
            compress_provider: this.ctx.compress_provider || '',
          },
        })
        toast('上下文设置已保存', 'ok')
        await this.load()
      } catch (e) { toast(errText(e), 'err') } finally { this.busy = '' }
    },
    async saveBot() {
      this.busy = 'bot'
      try {
        await call('rcbot.config.save', {
          bot: {
            enabled: !!this.bot.enabled,
            group_need_at: !!this.bot.group_need_at,
            private_always_reply: !!this.bot.private_always_reply,
            reply_with_mention: !!this.bot.reply_with_mention,
            reply_with_quote: this.bot.reply_with_quote !== false,
            reply_when_quoted: this.bot.reply_when_quoted !== false,
            wake_prefix: splitList(this.bot.__prefixText != null ? this.bot.__prefixText : (this.bot.wake_prefix || []).join(',')),
            allowed_groups: splitList(this.bot.__allowText != null ? this.bot.__allowText : (this.bot.allowed_groups || []).join(',')),
            blocked_groups: splitList(this.bot.__blockText != null ? this.bot.__blockText : (this.bot.blocked_groups || []).join(',')),
            rate_limit: {
              window: Number((this.bot.rate_limit || {}).window) || 60,
              max: Number((this.bot.rate_limit || {}).max) || 30,
            },
          },
        })
        toast('触发规则已保存', 'ok')
        await this.load()
      } catch (e) { toast(errText(e), 'err') } finally { this.busy = '' }
    },
    async saveFeat() {
      this.busy = 'feat'
      try {
        await call('rcbot.config.save', {
          features: {
            ai: { enabled: !!this.ai.enabled },
            panel: { enabled: !!this.pnl.enabled },
            web_search: {
              enabled: !!this.ws.enabled,
              max_results: Number(this.ws.max_results) || 5,
            },
            vision: {
              enabled: !!this.vis.enabled,
              max_images: Number(this.vis.max_images) || 3,
            },
            random_pick: {
              enabled: this.rp.enabled !== false,
              scope: this.rp.scope || 'enabled_groups',
              respect_need_at: !!this.rp.respect_need_at,
            },
            sl_status: {
              enabled: this.sl.enabled !== false,
              keyword: String(this.sl.keyword || '#sl').trim() || '#sl',
              cooldown: Math.max(1, Number(this.sl.cooldown) || 10),
            },
          },
        })
        toast('能力开关已保存', 'ok')
        await this.load()
      } catch (e) { toast(errText(e), 'err') } finally { this.busy = '' }
    },
    async saveConn() {
      this.busy = 'conn'
      try {
        await call('qqbot.conn.save', {
          config: {
            api: this.conn.config.api,
            timeout: Number(this.conn.config.timeout) || 90,
          },
        })
        toast('连接设置已保存', 'ok')
        await this.load()
      } catch (e) { toast(errText(e), 'err') } finally { this.busy = '' }
    },
    async testSearch() {
      const q = this.searchQ.trim()
      if (!q) return
      this.busy = 'search'
      this.searchOut = null
      try {
        const r = await callData('rcbot.tools.search', { q })
        this.searchOut = r || {}
      } catch (e) { toast(errText(e), 'err') } finally { this.busy = '' }
    },
  },
  template: `
  <div>
    <div v-if="err" class="rcq-pnl rcq-warn" style="font-size:12px">{{ err }}</div>
    <div class="rcq-pnl" v-if="!cfg"><div class="rcq-empty">读取配置中…</div></div>

    <div class="rcq-pnl" v-if="cfg">
      <div class="rcq-ph">
        <button class="btn btn-sm" :class="tab === 'ctx' ? 'btn-primary' : ''" @click="tab = 'ctx'">上下文与触发</button>
        <button class="btn btn-sm" :class="tab === 'cap' ? 'btn-primary' : ''" @click="tab = 'cap'">能力</button>
        <button class="btn btn-sm" :class="tab === 'conn' ? 'btn-primary' : ''" @click="tab = 'conn'">连接</button>
        <span class="sp"></span>
        <button class="btn btn-sm" :disabled="!!busy" @click="load">重新读取</button>
      </div>

      <!-- 上下文与触发 -->
      <div v-if="tab === 'ctx'">
        <div class="rcq-ph" style="margin-bottom:10px"><b>上下文</b>
          <span class="rcq-hint">决定它记得多少、什么时候压缩</span></div>
        <div class="rcq-form">
          <label class="rcq-fi"><span>模型上下文窗口（tokens）</span>
            <input class="input" type="number" v-model="ctx.max_tokens" /></label>
          <label class="rcq-fi"><span>最大输出（tokens）</span>
            <input class="input" type="number" v-model="ctx.max_output_tokens" /></label>
          <label class="rcq-fi"><span>保留最近比例</span>
            <input class="input" type="number" step="0.05" min="0.05" max="0.9" v-model="ctx.keep_recent_ratio" /></label>
          <label class="rcq-fi"><span>最多带多少条历史</span>
            <input class="input" type="number" v-model="ctx.max_history_messages" /></label>
        </div>
        <div class="switch-row">
          <label>启用上下文压缩（超预算时把旧对话压成摘要）</label>
          <label class="switch"><input type="checkbox" v-model="ctx.compress_enabled" /><span class="slider"></span></label>
        </div>
        <div class="rcq-note">
          预算 = 上下文窗口 − 最大输出 − 系统提示。超了就保留最近 {{ Math.round((ctx.keep_recent_ratio || 0) * 100) }}%，
          更旧的交给模型压成摘要。推理模型建议「最大输出」≥ 4096，否则思考就把预算吃光了。
        </div>
        <div class="rcq-flex" style="margin-top:12px">
          <button class="btn btn-primary btn-sm" :disabled="!!busy" @click="saveCtx">保存</button>
        </div>

        <div class="rcq-sec">
          <div class="rcq-ph" style="margin-bottom:10px"><b>触发规则</b>
            <span class="rcq-hint">什么消息才回</span></div>
          <div class="switch-row">
            <label>机器人总开关</label>
            <label class="switch"><input type="checkbox" v-model="bot.enabled" /><span class="slider"></span></label>
          </div>
          <div class="switch-row">
            <label>群里必须 @ 才回复</label>
            <label class="switch"><input type="checkbox" v-model="bot.group_need_at" /><span class="slider"></span></label>
          </div>
          <div class="switch-row">
            <label>私聊全部回复</label>
            <label class="switch"><input type="checkbox" v-model="bot.private_always_reply" /><span class="slider"></span></label>
          </div>
          <div class="switch-row">
            <label>回复时 @ 对方</label>
            <label class="switch"><input type="checkbox" v-model="bot.reply_with_mention" /><span class="slider"></span></label>
          </div>
          <div class="switch-row">
            <label>回复时引用原消息</label>
            <label class="switch"><input type="checkbox" v-model="bot.reply_with_quote" /><span class="slider"></span></label>
          </div>
          <div class="switch-row">
            <label>引用机器人消息时回复
              <div class="rcq-note">群里没 @ 但引用了机器人说的话，也算在跟它说话。</div>
            </label>
            <label class="switch"><input type="checkbox" v-model="bot.reply_when_quoted" /><span class="slider"></span></label>
          </div>
          <div class="rcq-form" style="margin-top:8px">
            <label class="rcq-fi"><span>唤醒前缀（逗号分隔，不用 @）</span>
              <input class="input" :value="(bot.wake_prefix || []).join(',')"
                @input="bot.__prefixText = $event.target.value" placeholder="/" /></label>
            <label class="rcq-fi"><span>限流：窗口（秒）</span>
              <input class="input" type="number" v-model="bot.rate_limit.window" /></label>
            <label class="rcq-fi"><span>限流：窗口内最多回复</span>
              <input class="input" type="number" v-model="bot.rate_limit.max" /></label>
            <label class="rcq-fi"><span>只回这些群（留空 = 不限）</span>
              <input class="input" :value="(bot.allowed_groups || []).join(',')"
                @input="bot.__allowText = $event.target.value" placeholder="群号，逗号分隔" /></label>
            <label class="rcq-fi"><span>屏蔽这些群</span>
              <input class="input" :value="(bot.blocked_groups || []).join(',')"
                @input="bot.__blockText = $event.target.value" placeholder="群号，逗号分隔" /></label>
          </div>
          <div class="rcq-flex" style="margin-top:12px">
            <button class="btn btn-primary btn-sm" :disabled="!!busy" @click="saveBot">保存</button>
          </div>
        </div>
      </div>

      <!-- 能力 -->
      <div v-if="tab === 'cap'">
        <div class="switch-row">
          <label>AI 回复
            <div class="rcq-note">关闭后普通消息不调用模型；面板菜单与功能仍可用。</div>
          </label>
          <label class="switch"><input type="checkbox" v-model="ai.enabled" /><span class="slider"></span></label>
        </div>
        <div class="switch-row">
          <label>菜单面板
            <div class="rcq-note">关闭后 @机器人 菜单 交给 AI 处理。</div>
          </label>
          <label class="switch"><input type="checkbox" v-model="pnl.enabled" /><span class="slider"></span></label>
        </div>
        <div class="switch-row">
          <label>允许联网搜索
            <div class="rcq-note">模型遇到时效性问题会调用 <code>web_search</code>，走 Bing 抓结果。</div>
          </label>
          <label class="switch"><input type="checkbox" v-model="ws.enabled" /><span class="slider"></span></label>
        </div>
        <div class="rcq-form" style="margin-top:6px">
          <label class="rcq-fi"><span>每次搜索取几条</span>
            <input class="input rcq-num" type="number" min="1" max="10" v-model="ws.max_results" /></label>
        </div>

        <div class="rcq-sec">
          <div class="switch-row">
            <label>允许识图
              <div class="rcq-note">消息里有图片时，把图转成 base64 直接喂给模型（不用另配视觉模型）。</div>
            </label>
            <label class="switch"><input type="checkbox" v-model="vis.enabled" /><span class="slider"></span></label>
          </div>
          <div class="rcq-form" style="margin-top:6px">
            <label class="rcq-fi"><span>单条消息最多看几张</span>
              <input class="input rcq-num" type="number" min="1" max="6" v-model="vis.max_images" /></label>
          </div>
<div class="rcq-note">
          只有「当前这轮」会带图，历史里只留 [图片] 文本 —— 不然每轮都要重传图片，token 会爆。
          </div>
        </div>

        <div class="rcq-sec">
          <div class="switch-row">
            <label>允许随机挑消息回
              <div class="rcq-note">
                消息页的 🎲：从群聊里随机翻一条别人说过的话，让机器人对它回一句。
                点「发送到 QQ」会真的发到那个群里（并 @ 原说话人）。
              </div>
            </label>
            <label class="switch"><input type="checkbox" v-model="rp.enabled" /><span class="slider"></span></label>
          </div>
          <div class="rcq-form" style="margin-top:6px">
            <label class="rcq-fi"><span>从哪里挑</span>
              <select class="input" v-model="rp.scope">
                <option value="enabled_groups">已启用的群聊（推荐）</option>
                <option value="all_groups">所有群聊</option>
              </select>
            </label>
          </div>
          <div class="switch-row">
            <label>随机挑也遵守「群里必须 @」
              <div class="rcq-note">
                开启后只挑 @过机器人（或带唤醒前缀）的消息，避免和「群里必须 @ 才回复」冲突；
                关闭 = 随机挑是手动触发，不受这条规则限制。
              </div>
            </label>
            <label class="switch"><input type="checkbox" v-model="rp.respect_need_at" /><span class="slider"></span></label>
          </div>
          <div class="rcq-note">
            「已启用的群聊」= 在「会话管理」里打开开关的那些群。还没启用的群不参与挑选。
            挑选不是纯随机：按「长度合适、像在问话、比较新、各群轮换」加权，避免翻到
            <code>[图片]</code>、单字回复或反复同一群。
          </div>
        </div>

        <div class="rcq-sec">
          <div class="switch-row">
            <label>允许 #sl 状态指令
              <div class="rcq-note">
                任意群聊 / 私聊里发 <b>#sl</b>，机器人回一条 SnowLuma 状态
                （容器、QQ 登录、OneBot 连接、消息档案条数）。
                关掉后 #sl 只是普通消息，走正常的 @ / 唤醒规则。
              </div>
            </label>
            <label class="switch"><input type="checkbox" v-model="sl.enabled" /><span class="slider"></span></label>
          </div>
          <div class="rcq-form" style="margin-top:6px">
            <label class="rcq-fi"><span>触发关键词</span>
              <input class="input" v-model="sl.keyword" placeholder="#sl" /></label>
            <label class="rcq-fi"><span>冷却（秒）</span>
              <input class="input rcq-num" type="number" min="1" max="600" v-model="sl.cooldown" /></label>
          </div>
          <div class="rcq-note">同一会话在冷却时间内只回一次，避免群里刷屏。</div>
        </div>

        <div class="rcq-flex" style="margin-top:12px">
          <button class="btn btn-primary btn-sm" :disabled="!!busy" @click="saveFeat">保存</button>
        </div>

        <div class="rcq-sec">
          <div class="rcq-ph" style="margin-bottom:10px"><b>试一下搜索</b>
            <span class="rcq-hint">验证 Bing 通道通不通</span></div>
          <div class="rcq-flex">
            <input class="input" style="flex:1;min-width:160px" v-model="searchQ"
              @keyup.enter="testSearch" placeholder="例如：杭州天气" />
            <button class="btn btn-sm" :disabled="busy === 'search'" @click="testSearch">搜索</button>
          </div>
          <div v-if="searchOut" style="margin-top:10px">
            <div class="rcq-list">
              <div class="rcq-row" v-for="(r, i) in (searchOut.results || [])" :key="i">
                <div class="main">
                  <div class="t">{{ r.title }}</div>
                  <div class="d" style="white-space:normal">{{ r.snippet }}</div>
                  <div class="d rcq-mono">{{ r.url }}</div>
                </div>
              </div>
              <div v-if="!(searchOut.results || []).length" class="rcq-empty">没有结果</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 连接 -->
      <div v-if="tab === 'conn' && conn">
        <div class="rcq-ph" style="margin-bottom:10px"><b>SnowLuma（协议端）</b><span class="sp"></span>
          <span class="rcq-lamp"><b :class="conn.snowluma && conn.snowluma.ok ? 'on' : 'off'"></b>
            {{ conn.snowluma && conn.snowluma.ok ? '容器在运行' : '容器未运行' }}</span></div>
        <div class="rcq-note" v-if="conn.snowluma && conn.snowluma.error">{{ conn.snowluma.error }}</div>
        <div class="rcq-note">
          QQ 跑在 Docker 容器 <code>snowluma</code> 里（OneBot WS 3001 / HTTP 3000 / noVNC 6081）。
          容器没起就去「QQ 账户」点「启动」或「扫码登录」。
        </div>

        <div class="rcq-sec">
          <div class="rcq-ph" style="margin-bottom:10px"><b>rcbot（机器人）</b><span class="sp"></span>
            <span class="rcq-lamp"><b :class="conn.rcbot && conn.rcbot.ok ? 'on' : 'off'"></b>
              {{ conn.rcbot && conn.rcbot.ok ? '已连通' : '连不上' }}</span></div>
          <div class="rcq-form">
            <label class="rcq-fi wide"><span>HTTP 地址</span>
              <input class="input" v-model="conn.config.api" placeholder="http://127.0.0.1:6710" /></label>
            <label class="rcq-fi"><span>请求超时（秒）</span>
              <input class="input" type="number" v-model="conn.config.timeout" /></label>
          </div>
          <div class="rcq-note" v-if="conn.rcbot && conn.rcbot.error">{{ conn.rcbot.error }}</div>
        </div>

        <div class="rcq-flex" style="margin-top:12px">
          <button class="btn btn-primary btn-sm" :disabled="!!busy" @click="saveConn">保存</button>
          <span class="rcq-hint">插件版本 v{{ conn.version }}</span>
        </div>
      </div>
    </div>
  </div>`,
}

// ------------------------------------------------------------------ 框架

// ------------------------------------------------------------------ 工具链

const Tools = {
  data() {
    return {
      loading: true, busy: '', err: '', tools: [], enabled: {},
      ws: { root: '', files: 0, bytes: 0, max_mb: 20 },
      fsPath: '', fsItems: [], edit: null, test: null, testOut: '',
    }
  },
  async mounted() { await this.load() },
  methods: {
    fmtSize(n) {
      n = Number(n) || 0
      if (n >= 1048576) return (n / 1048576).toFixed(1) + ' MB'
      if (n >= 1024) return Math.round(n / 1024) + ' KB'
      return n + ' B'
    },
    async load() {
      this.loading = true
      try {
        const d = await callData('qqbot.tools.get', {})
        this.tools = (d && d.tools) || []
        this.enabled = (d && d.enabled) || {}
        this.ws = (d && d.workspace) || this.ws
        await this.fsList(this.fsPath)
      } catch (e) { this.err = errText(e) } finally { this.loading = false }
    },
    async saveCfg() {
      this.busy = 'save'
      try {
        await callData('qqbot.tools.save', {
          enabled: this.enabled,
          workspace: { max_mb: Number(this.ws.max_mb) || 20 },
        })
        toast('工具链设置已保存', 'ok')
      } catch (e) { toast(errText(e), 'err') } finally { this.busy = '' }
    },
    async fsList(rel) {
      try {
        const d = await callData('qqbot.tools.fs', { action: 'list', path: rel || '' })
        this.fsPath = (d && d.path) || ''
        this.fsItems = (d && d.items) || []
      } catch (e) { toast(errText(e), 'err') }
    },
    fsGo(it) {
      if (it.is_dir) this.fsList((this.fsPath ? this.fsPath + '/' : '') + it.name)
      else this.openFile(it.name)
    },
    fsUp() {
      const parts = this.fsPath.split('/').filter(Boolean)
      parts.pop()
      this.fsList(parts.join('/'))
    },
    async openFile(name) {
      const path = (this.fsPath ? this.fsPath + '/' : '') + name
      try {
        const d = await callData('qqbot.tools.fs', { action: 'read', path })
        this.edit = { path, content: (d && d.content) || '', size: (d && d.size) || 0 }
      } catch (e) { toast(errText(e), 'err') }
    },
    newFile() {
      const name = prompt('文件名（可带子目录，如 notes/todo.txt）')
      if (!name) return
      this.edit = { path: (this.fsPath ? this.fsPath + '/' : '') + name, content: '', size: 0 }
    },
    async newDir() {
      const name = prompt('目录名')
      if (!name) return
      try {
        await callData('qqbot.tools.fs', { action: 'mkdir', path: (this.fsPath ? this.fsPath + '/' : '') + name })
        await this.fsList(this.fsPath)
      } catch (e) { toast(errText(e), 'err') }
    },
    async saveFile() {
      if (!this.edit) return
      try {
        await callData('qqbot.tools.fs', { action: 'write', path: this.edit.path, content: this.edit.content })
        toast('已保存', 'ok')
        this.edit = null
        await this.load()
      } catch (e) { toast(errText(e), 'err') }
    },
    async delItem(it) {
      const path = (this.fsPath ? this.fsPath + '/' : '') + it.name
      if (!confirm('删除「' + path + '」？')) return
      try {
        await callData('qqbot.tools.fs', { action: 'delete', path })
        await this.load()
      } catch (e) { toast(errText(e), 'err') }
    },
    openTest(t) {
      const preset = {
        web_search: { query: '今天的新闻' },
        calc: { expression: 'sqrt(2)*10 + 3**2' },
        convert: { value: 100, from: 'km', to: 'mi' },
        random: { kind: 'dice', sides: 6, count: 2 },
        codec: { action: 'sha256', text: 'hello' },
        date_calc: { action: 'diff', date1: '2026-01-01', date2: '2026-11-08' },
      }
      this.test = { id: t.id, args: JSON.stringify(preset[t.id] || {}, null, 2) }
      this.testOut = ''
    },
    async runTest() {
      if (!this.test) return
      this.busy = 'test'
      try {
        const args = JSON.parse(this.test.args || '{}')
        const d = await callData('qqbot.tools.test', { id: this.test.id, args })
        this.testOut = JSON.stringify(d && d.result, null, 2)
      } catch (e) { this.testOut = '失败：' + errText(e) } finally { this.busy = '' }
    },
  },
  template: `
  <div>
    <div v-if="err" class="rcq-pnl rcq-warn" style="font-size:12px">{{ err }}</div>

    <div class="rcq-pnl">
      <div class="rcq-flex">
        <b>系统内置工具</b>
        <span class="rcq-hint">AI 按需调用；只做系统内置，不开放自定义</span>
        <span style="margin-left:auto"></span>
        <button class="btn btn-sm btn-primary" :disabled="!!busy" @click="saveCfg">保存</button>
      </div>
      <div v-for="t in tools" :key="t.id" class="rcq-flex"
        style="padding:9px 0;border-bottom:1px solid var(--bd)">
        <label class="switch"><input type="checkbox" v-model="enabled[t.id]" /><span class="slider"></span></label>
        <b style="margin-left:8px">{{ t.name }}</b>
        <span class="rcq-hint" style="margin-left:6px">{{ t.desc }}</span>
        <span style="margin-left:auto"></span>
        <span class="rcq-badge" :class="t.category === 'workspace' ? 'warn' : 'ok'">
          {{ t.category === 'workspace' ? '工作区' : '辅助' }}</span>
        <button class="btn btn-sm" style="margin-left:8px" @click="openTest(t)">测试</button>
      </div>
    </div>

    <div class="rcq-pnl">
      <div class="rcq-flex">
        <b>工作区</b>
        <span class="rcq-hint">{{ ws.files }} 个文件 · {{ fmtSize(ws.bytes) }} / {{ ws.max_mb }} MB</span>
        <span style="margin-left:auto"></span>
        <label class="rcq-hint">配额(MB)</label>
        <input class="input" type="number" min="1" max="1024" style="width:90px" v-model.number="ws.max_mb" />
        <button class="btn btn-sm" @click="saveCfg">应用</button>
      </div>
      <div class="rcq-note" style="word-break:break-all">
        {{ ws.root }} —— AI 只能在这个目录内读写，初始为空。
      </div>
      <div class="rcq-flex" style="margin-top:8px">
        <button class="btn btn-sm" @click="fsUp" :disabled="!fsPath">↑ 上一级</button>
        <span class="rcq-hint" style="margin-left:6px">/{{ fsPath }}</span>
        <span style="margin-left:auto"></span>
        <button class="btn btn-sm" @click="newFile">新建文件</button>
        <button class="btn btn-sm" @click="newDir">新建目录</button>
        <button class="btn btn-sm" @click="fsList(fsPath)">刷新</button>
      </div>
      <div v-for="it in fsItems" :key="it.name" class="rcq-flex"
        style="padding:7px 0;border-bottom:1px solid var(--bd)">
        <span style="cursor:pointer" @click="fsGo(it)">
          {{ it.is_dir ? '📁' : '📄' }} {{ it.name }}</span>
        <span class="rcq-hint" style="margin-left:auto">{{ it.is_dir ? '' : fmtSize(it.size) }}</span>
        <button class="btn btn-sm" style="margin-left:8px" @click="delItem(it)">删除</button>
      </div>
      <div v-if="!fsItems.length" class="rcq-hint" style="margin-top:8px">空目录</div>
    </div>

    <div v-if="edit" class="rcq-mask" @click.self="edit = null">
      <div class="rcq-modal">
        <div class="rcq-flex"><b class="mono" style="word-break:break-all">{{ edit.path }}</b>
          <span style="margin-left:auto"></span>
          <button class="btn btn-sm" @click="edit = null">关闭</button></div>
        <textarea class="input" rows="16" v-model="edit.content" style="margin-top:10px"></textarea>
        <div class="rcq-acts" style="margin-top:10px">
          <button class="btn btn-primary" @click="saveFile">保存</button>
          <button class="btn" @click="edit = null">取消</button>
        </div>
      </div>
    </div>

    <div v-if="test" class="rcq-mask" @click.self="test = null">
      <div class="rcq-modal">
        <div class="rcq-flex"><b>测试 {{ test.id }}</b>
          <span style="margin-left:auto"></span>
          <button class="btn btn-sm" @click="test = null">关闭</button></div>
        <div class="rcq-fi" style="margin-top:10px"><span>参数（JSON）</span>
          <textarea class="input" rows="4" v-model="test.args"></textarea></div>
        <div class="rcq-acts" style="margin-top:10px">
          <button class="btn btn-primary" :disabled="busy === 'test'" @click="runTest">运行</button>
        </div>
        <pre v-if="testOut" style="margin-top:10px;white-space:pre-wrap;max-height:260px;overflow:auto;background:var(--sf2);padding:10px;border-radius:8px;font-size:12px">{{ testOut }}</pre>
      </div>
    </div>
  </div>`,
}

// ------------------------------------------------------------------ 面板

const PanelPage = {
  data() {
    return {
      tab: 'menu', loading: true, busy: '', err: '',
      cfg: null, images: {}, previewText: '',
      edit: null, selPool: '', selImg: '',
    }
  },
  computed: {
    items() { return (this.cfg && this.cfg.items) || [] },
    pools() { return (this.cfg && this.cfg.text_pools) || [] },
    ipools() { return (this.cfg && this.cfg.image_pools) || [] },
    curPool() { return this.pools.find((p) => p.id === this.selPool) || this.pools[0] || null },
    curImg() { return this.ipools.find((p) => p.id === this.selImg) || this.ipools[0] || null },
  },
  async mounted() { await this.load() },
  methods: {
    async load() {
      this.loading = true
      try {
        const d = await callData('qqbot.panel.get', {})
        this.cfg = (d && d.panel) || { items: [], text_pools: [], image_pools: [] }
        this.images = (d && d.images) || {}
        if (!this.selPool) this.selPool = (this.cfg.text_pools[0] || {}).id || ''
        if (!this.selImg) this.selImg = (this.cfg.image_pools[0] || {}).id || ''
      } catch (e) { this.err = errText(e) } finally { this.loading = false }
    },
    async save() {
      this.busy = 'save'
      try {
        await callData('qqbot.panel.save', { panel: this.cfg })
        toast('面板已保存', 'ok')
      } catch (e) { toast(errText(e), 'err') } finally { this.busy = '' }
    },
    async previewMenu() {
      try {
        const d = await callData('qqbot.panel.preview', { mode: 'menu' })
        this.previewText = (d && d.text) || ''
      } catch (e) { toast(errText(e), 'err') }
    },
    async previewItem(it) {
      try {
        const d = await callData('qqbot.panel.preview', { mode: 'feature', id: it.id })
        this.previewText = ((d && d.text) || '') + (d && d.image ? '\n[图片] ' + d.image : '')
      } catch (e) { toast(errText(e), 'err') }
    },
    addItem() {
      this.edit = {
        id: 'item_' + Date.now().toString(36), name: '', aliases: [], desc: '',
        type: 'content', text_pool: (this.pools[0] || {}).id || '',
        image_pool: (this.ipools[0] || {}).id || '', cooldown: 5,
        show_in_menu: true, enabled: true, text: '',
      }
    },
    editItem(it) { this.edit = JSON.parse(JSON.stringify(it)) },
    saveEdit() {
      const e = this.edit
      if (!e || !String(e.name || '').trim()) { toast('名称不能为空', 'err'); return }
      const i = this.items.findIndex((x) => x.id === e.id)
      if (i >= 0) this.cfg.items.splice(i, 1, e)
      else this.cfg.items.push(e)
      this.edit = null
      this.save()
    },
    delItem(i) {
      if (!confirm('删除功能项「' + (this.items[i].name || '') + '」？')) return
      this.cfg.items.splice(i, 1)
      this.save()
    },
    moveItem(i, d) {
      const j = i + d
      if (j < 0 || j >= this.items.length) return
      const t = this.cfg.items[i]
      this.cfg.items[i] = this.cfg.items[j]
      this.cfg.items[j] = t
      this.save()
    },
    aliasesStr(it) { return (it.aliases || []).join(', ') },
    setAliases(it, v) { it.aliases = String(v || '').split(/[,，\s]+/).filter(Boolean) },
    levelsStr(it) { return (it.levels || []).join(', ') },
    setLevels(it, v) { it.levels = String(v || '').split(/[,，\s]+/).filter(Boolean) },
    poolText(pool) {
      return (pool.items || []).filter((x) => !x.source || x.source === 'manual')
        .map((x) => (typeof x === 'string' ? x : x.text || '')).join('\n')
    },
    setPoolText(pool, v) {
      const ai = (pool.items || []).filter((x) => x.source === 'ai')
      const lines = String(v || '').split('\n').map((s) => s.trim()).filter(Boolean)
      pool.items = lines.map((t, i) => ({ id: 'm' + i, text: t, source: 'manual' })).concat(ai)
    },
    aiOf(pool) {
      if (!pool.ai_daily) pool.ai_daily = { enabled: false, count: 10, time: '00:10', keep_max: 300 }
      return pool.ai_daily
    },
    addTextPool() {
      const id = 'pool_' + Date.now().toString(36)
      this.cfg.text_pools = this.cfg.text_pools || []
      this.cfg.text_pools.push({
        id, name: '新文本组', enabled: true, items: [],
        ai_daily: { enabled: false, count: 10, time: '00:10', keep_max: 300, prompt: '' },
      })
      this.selPool = id
      this.save()
    },
    delTextPool() {
      const p = this.curPool
      if (!p || !confirm('删除文本组「' + p.name + '」？')) return
      this.cfg.text_pools = this.pools.filter((x) => x.id !== p.id)
      this.selPool = (this.cfg.text_pools[0] || {}).id || ''
      this.save()
    },
    addImgPool() {
      const id = 'img_' + Date.now().toString(36)
      this.cfg.image_pools = this.cfg.image_pools || []
      this.cfg.image_pools.push({
        id, name: '新图片组', enabled: true, source: 'api', items: [],
        api: { url: '', timeout: 10, max_bytes: 8388608, max_redirects: 3 },
      })
      this.selImg = id
      this.save()
    },
    delImgPool() {
      const p = this.curImg
      if (!p || !confirm('删除图片组「' + p.name + '」？')) return
      this.cfg.image_pools = this.ipools.filter((x) => x.id !== p.id)
      this.selImg = (this.cfg.image_pools[0] || {}).id || ''
      this.save()
    },
    async generate(pool) {
      this.busy = 'gen'
      try {
        const d = await callData('qqbot.panel.generate', {
          pool_id: pool.id, count: Number(this.aiOf(pool).count) || 10,
        }, { timeoutMs: 180000 })
        toast('已生成 ' + ((d && d.added) || 0) + ' 条', 'ok')
        await this.load()
      } catch (e) { toast(errText(e), 'err') } finally { this.busy = '' }
    },
    async uploadImage(ev) {
      const f = ev.target.files && ev.target.files[0]
      ev.target.value = ''
      if (!f || !this.curImg) return
      const b64 = await new Promise((res) => {
        const r = new FileReader()
        r.onload = () => res(String(r.result || ''))
        r.readAsDataURL(f)
      })
      this.busy = 'upload'
      try {
        const d = await callData('qqbot.panel.image_upload', {
          pool_id: this.curImg.id, name: f.name, data: b64,
        })
        if (d && d.name) {
          this.curImg.items = this.curImg.items || []
          this.curImg.items.push(d.name)
          await this.save()
        }
        await this.load()
        toast('已上传', 'ok')
      } catch (e) { toast(errText(e), 'err') } finally { this.busy = '' }
    },
    imgUrl(name) {
      const list = this.images[(this.curImg || {}).id] || []
      const hit = list.find((x) => x.name === name)
      return hit ? '/api/fm/preview?path=' + encodeURIComponent(hit.abs) : ''
    },
    fmtSize(n) {
      n = Number(n) || 0
      return n >= 1048576 ? (n / 1048576).toFixed(1) + 'MB' : Math.round(n / 1024) + 'KB'
    },
  },
  template: `
  <div>
    <div v-if="err" class="rcq-pnl rcq-warn" style="font-size:12px">{{ err }}</div>

    <div class="rcq-pnl">
      <div class="rcq-flex">
        <button class="btn btn-sm" :class="tab === 'menu' ? 'btn-primary' : ''" @click="tab = 'menu'">菜单</button>
        <button class="btn btn-sm" :class="tab === 'text' ? 'btn-primary' : ''" @click="tab = 'text'">文本库</button>
        <button class="btn btn-sm" :class="tab === 'image' ? 'btn-primary' : ''" @click="tab = 'image'">图片库</button>
        <span style="margin-left:auto"></span>
        <button class="btn btn-sm btn-primary" :disabled="!!busy" @click="save">
          {{ busy === 'save' ? '保存中…' : '保存' }}</button>
      </div>
    </div>

    <template v-if="tab === 'menu' && cfg">
      <div class="rcq-pnl">
        <div class="rcq-grid">
          <label class="rcq-fi"><span>标题</span>
            <input class="input" v-model="cfg.title" /></label>
          <label class="rcq-fi"><span>触发词（逗号分隔）</span>
            <input class="input" :value="(cfg.triggers || []).join(', ')"
              @input="cfg.triggers = $event.target.value.split(/[,，\\s]+/).filter(Boolean)" /></label>
          <label class="rcq-fi"><span>底部提示</span>
            <input class="input" v-model="cfg.hint" /></label>
          <div class="rcq-acts">
            <label class="rcq-fi" style="margin:0"><span>每页条数</span>
              <input class="input" type="number" min="1" max="20" v-model.number="cfg.page_size" style="width:90px" /></label>
            <button class="btn btn-sm" @click="previewMenu">预览菜单</button>
            <button class="btn btn-sm" @click="addItem">+ 功能</button>
          </div>
        </div>
        <pre v-if="previewText" style="margin-top:10px;white-space:pre-wrap;background:var(--sf2);padding:10px;border-radius:8px;font-size:12.5px">{{ previewText }}</pre>
      </div>

      <div class="rcq-pnl">
        <div v-for="(it, i) in items" :key="it.id" class="rcq-flex"
          style="padding:9px 0;border-bottom:1px solid var(--bd)">
          <b style="min-width:110px">{{ it.name || '(未命名)' }}</b>
          <span class="rcq-hint">{{ it.type }}<template v-if="it.aliases && it.aliases.length"> · {{ aliasesStr(it) }}</template></span>
          <span style="margin-left:auto"></span>
          <button class="btn btn-sm" @click="moveItem(i, -1)" :disabled="i === 0">↑</button>
          <button class="btn btn-sm" @click="moveItem(i, 1)" :disabled="i === items.length - 1">↓</button>
          <button class="btn btn-sm" @click="previewItem(it)">预览</button>
          <button class="btn btn-sm" @click="editItem(it)">编辑</button>
          <button class="btn btn-sm" @click="delItem(i)">删除</button>
        </div>
        <div v-if="!items.length" class="rcq-empty2">还没有功能项</div>
      </div>
    </template>

    <template v-if="tab === 'text' && cfg">
      <div class="rcq-pnl">
        <div class="rcq-flex">
          <select class="input" style="width:220px" v-model="selPool">
            <option v-for="p in pools" :key="p.id" :value="p.id">{{ p.name }}（{{ (p.items || []).length }} 条）</option>
          </select>
          <button class="btn btn-sm" @click="addTextPool">+ 新建</button>
          <button class="btn btn-sm" @click="delTextPool">删除</button>
          <span style="margin-left:auto"></span>
          <button class="btn btn-sm" :disabled="busy === 'gen'" @click="generate(curPool)">
            {{ busy === 'gen' ? '生成中…' : '立即生成' }}</button>
        </div>
      </div>

      <div v-if="curPool" class="rcq-pnl">
        <label class="rcq-fi"><span>文本组名称</span>
          <input class="input" v-model="curPool.name" /></label>
        <div class="rcq-fi" style="margin-top:10px"><span>文案（每行一条；AI 生成的条目在下方单独列出）</span>
          <textarea class="input" rows="10" :value="poolText(curPool)"
            @input="setPoolText(curPool, $event.target.value)"></textarea></div>

        <div class="rcq-flex" style="margin-top:12px">
          <b>AI 每日生成</b>
          <label class="rcq-hint"><input type="checkbox" v-model="aiOf(curPool).enabled" /> 启用</label>
          <span class="rcq-hint">每天</span>
          <input class="input" style="width:90px" v-model="aiOf(curPool).time" placeholder="00:10" />
          <span class="rcq-hint">生成</span>
          <input class="input" type="number" min="1" max="50" style="width:80px" v-model.number="aiOf(curPool).count" />
          <span class="rcq-hint">条 · 保留上限</span>
          <input class="input" type="number" min="0" style="width:90px" v-model.number="aiOf(curPool).keep_max" />
        </div>
        <div class="rcq-fi" style="margin-top:8px"><span>生成提示词（留空用默认）</span>
          <textarea class="input" rows="3" v-model="aiOf(curPool).prompt"></textarea></div>
        <div class="rcq-hint" style="margin-top:6px">
          上次：{{ aiOf(curPool).last_run_date || '—' }} · {{ aiOf(curPool).last_run_count || 0 }} 条
        </div>

        <div v-if="(curPool.items || []).some(x => x.source === 'ai')" style="margin-top:12px">
          <b>AI 条目</b>
          <div v-for="(x, i) in (curPool.items || [])" :key="i">
            <div v-if="x.source === 'ai'" class="rcq-flex" style="padding:6px 0;border-bottom:1px solid var(--bd)">
              <span style="font-size:12.5px">{{ x.text }}</span>
              <span class="rcq-hint" style="margin-left:8px;flex:none">{{ x.gen_date }}</span>
              <span style="margin-left:auto"></span>
              <button class="btn btn-sm" @click="curPool.items.splice(i, 1); save()">删除</button>
            </div>
          </div>
        </div>
      </div>
    </template>

    <template v-if="tab === 'image' && cfg">
      <div class="rcq-pnl">
        <div class="rcq-flex">
          <select class="input" style="width:220px" v-model="selImg">
            <option v-for="p in ipools" :key="p.id" :value="p.id">{{ p.name }}（{{ p.source }}）</option>
          </select>
          <button class="btn btn-sm" @click="addImgPool">+ 新建</button>
          <button class="btn btn-sm" @click="delImgPool">删除</button>
          <span style="margin-left:auto"></span>
          <label class="btn btn-sm" style="margin:0">上传图片
            <input type="file" accept="image/*" hidden @change="uploadImage" /></label>
        </div>
      </div>

      <div v-if="curImg" class="rcq-pnl">
        <div class="rcq-grid">
          <label class="rcq-fi"><span>图片组名称</span>
            <input class="input" v-model="curImg.name" /></label>
          <label class="rcq-fi"><span>来源</span>
            <select class="input" v-model="curImg.source">
              <option value="api">外部图片 API</option>
              <option value="local">本地图片</option>
            </select></label>
        </div>
        <div v-if="curImg.source === 'api'" class="rcq-grid" style="margin-top:10px">
          <label class="rcq-fi" style="grid-column:1/-1"><span>API 地址（302 最多跟 3 跳）</span>
            <input class="input" v-model="curImg.api.url" placeholder="https://www.loliapi.com/acg/pe/" /></label>
          <label class="rcq-fi"><span>超时（秒）</span>
            <input class="input" type="number" v-model.number="curImg.api.timeout" /></label>
          <label class="rcq-fi"><span>最大体积（MB）</span>
            <input class="input" type="number" :value="Math.round((curImg.api.max_bytes || 8388608) / 1048576)"
              @input="curImg.api.max_bytes = (Number($event.target.value) || 8) * 1048576" /></label>
        </div>
        <div v-else style="margin-top:10px">
          <div style="display:flex;flex-wrap:wrap;gap:8px">
            <div v-for="n in (curImg.items || [])" :key="n" style="width:110px">
              <img :src="imgUrl(n)" style="width:100%;height:80px;object-fit:cover;border-radius:8px"
                @error="$event.target.style.opacity = 0.25" />
              <div class="rcq-flex" style="margin-top:4px">
                <span class="rcq-hint" style="overflow:hidden;text-overflow:ellipsis">{{ n }}</span>
                <button class="btn btn-sm" style="margin-left:auto" @click="curImg.items = curImg.items.filter(v => v !== n); save()">×</button>
              </div>
            </div>
          </div>
          <div v-if="!(curImg.items || []).length" class="rcq-hint" style="margin-top:6px">还没有本地图片，点右上角上传</div>
        </div>
      </div>
    </template>

    <div v-if="edit" class="rcq-mask" @click.self="edit = null">
      <div class="rcq-modal">
        <div class="rcq-flex"><b>功能项</b><span style="margin-left:auto"></span>
          <button class="btn btn-sm" @click="edit = null">关闭</button></div>
        <div class="rcq-grid" style="margin-top:10px">
          <label class="rcq-fi"><span>名称</span><input class="input" v-model="edit.name" /></label>
          <label class="rcq-fi"><span>别名（逗号分隔）</span>
            <input class="input" :value="aliasesStr(edit)" @input="setAliases(edit, $event.target.value)" /></label>
          <label class="rcq-fi"><span>说明</span><input class="input" v-model="edit.desc" /></label>
          <label class="rcq-fi"><span>类型</span>
            <select class="input" v-model="edit.type">
              <option value="content">文本库 + 图片库</option>
              <option value="text">固定文本</option>
            </select></label>
          <label class="rcq-fi"><span>文本组</span>
            <select class="input" v-model="edit.text_pool">
              <option value="">不使用</option>
              <option v-for="p in pools" :key="p.id" :value="p.id">{{ p.name }}</option>
            </select></label>
          <label class="rcq-fi"><span>图片组</span>
            <select class="input" v-model="edit.image_pool">
              <option value="">不使用</option>
              <option v-for="p in ipools" :key="p.id" :value="p.id">{{ p.name }}</option>
            </select></label>
          <label class="rcq-fi"><span>冷却（秒）</span>
            <input class="input" type="number" v-model.number="edit.cooldown" /></label>
          <template v-if="edit.type === 'content'">
            <label class="rcq-fi"><span>运势等级（逗号分隔，留空不显示）</span>
              <input class="input" :value="levelsStr(edit)" @input="setLevels(edit, $event.target.value)" /></label>
            <label class="rcq-fi"><span>等级前缀</span>
              <input class="input" v-model="edit.level_prefix" placeholder="运势" /></label>
          </template>
          <label class="rcq-fi"><span>菜单显示</span>
            <label class="rcq-hint"><input type="checkbox" v-model="edit.show_in_menu" /> 显示</label></label>
        </div>
        <div v-if="edit.type === 'text'" class="rcq-fi" style="margin-top:10px">
          <span>固定文本</span><textarea class="input" rows="4" v-model="edit.text"></textarea></div>
        <div class="rcq-acts" style="margin-top:12px">
          <button class="btn btn-primary" @click="saveEdit">保存</button>
          <button class="btn" @click="edit = null">取消</button>
        </div>
      </div>
    </div>
  </div>`,
}

const TABS = [
  // 「消息」不再整屏铺满：和其它页签一样嵌在插件页里，
  // 顶部选项卡始终保留，用户随时能切走。
  { id: 'im', label: '消息', comp: IM },
  { id: 'overview', label: '概览', comp: Overview },
  { id: 'account', label: 'QQ 账户', comp: Accounts },
  { id: 'query', label: '查询', comp: Query },
  { id: 'media', label: '媒体库', comp: MediaLib },
  { id: 'cards', label: '角色卡片', comp: Cards },
  { id: 'sessions', label: '会话管理', comp: Sessions },
  { id: 'providers', label: '模型提供商', comp: Providers },
  { id: 'tools', label: '工具链', comp: Tools },
  { id: 'panel', label: '面板', comp: PanelPage },
  { id: 'logs', label: '运行日志', comp: Logs },
  { id: 'settings', label: '设置', comp: Settings },
]

const App = {
  data() {
    let tab = 'overview'
    try {
      const t = localStorage.getItem(LS_TAB)
      if (t && TABS.some((x) => x.id === t)) tab = t
    } catch (e) {}
    return { S, tab, TABS, conn: null, key: 0 }
  },
  computed: {
    cur() { return (this.TABS.find((t) => t.id === this.tab) || this.TABS[0]).comp },
    slOn() { return !!(this.conn && this.conn.snowluma && this.conn.snowluma.ok) },
    rbOn() { return !!(this.conn && this.conn.rcbot && this.conn.rcbot.ok) },
  },
  async mounted() { await this.check() },
  methods: {
    async check() {
      try { this.conn = await call('qqbot.conn.get') } catch (e) {}
    },
    go(id) {
      this.tab = id
      try { localStorage.setItem(LS_TAB, id) } catch (e) {}
      this.check()
    },
    // 消息页退出：回到概览，并把记忆的 tab 也改掉 ——
    // 否则刷新页面又直接铺满整屏，用户会以为卡住了
    onImClose() { this.go('overview') },
    refresh() {
      this.key++
      this.check()
    },
  },
  template: `
  <div class="rcq" :class="{ 'rcq-im-mode': tab === 'im' }">
    <div class="rcq-bar">
      <div class="rcq-tab" v-for="t in TABS" :key="t.id" :class="{ on: tab === t.id }"
        @click="go(t.id)">{{ t.label }}</div>
      <div class="rcq-bar-r">
        <span class="rcq-lamp"><b :class="slOn ? 'on' : 'off'"></b>SnowLuma</span>
        <span class="rcq-lamp"><b :class="rbOn ? 'on' : 'off'"></b>Bot</span>
        <button class="btn btn-sm" @click="refresh">刷新</button>
      </div>
    </div>

    <component :is="cur" :key="tab + '-' + key" @close="onImClose" />

    <div class="rcq-toast" v-if="S.toast" :class="S.toastKind">{{ S.toast }}</div>
  </div>`,
}

function mount(container, ctx) {
  injectStyle()
  injectIMStyle()
  CTX = ctx
  setIMCtx(ctx)
  const vm = createApp(App)
  const stop = () => { try { vm.unmount() } catch (e) {} }
  vm.mount(container)
  return stop
}

export function register(g) {
  g.__rcPluginV4__ = g.__rcPluginV4__ || {}
  g.__rcPluginV4__[NAME] = { pages: [{ path: '', title: 'QQ Bot' }], mount }
}
if (typeof window !== 'undefined') register(window)
