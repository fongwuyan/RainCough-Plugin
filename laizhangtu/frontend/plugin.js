// laizhangtu 插件前端（接口库 v4）：搜索结果 / 取图 / 历史 / 设置 / 缓存
// 由原 QQ 脚本插件 settings.html 的配置项迁移；构建产物 assets/plugin.js 内联 Vue。
import { createApp, h } from 'vue'

const NAME = 'laizhangtu'
const IFACE = {
  info: 'laizhangtu.info',
  configGet: 'laizhangtu.config.get',
  configSave: 'laizhangtu.config.save',
  fetch: 'laizhangtu.fetch',
  search: 'laizhangtu.search',
  pick: 'laizhangtu.pick',
  historyList: 'laizhangtu.history.list',
  historyClear: 'laizhangtu.history.clear',
  cacheStats: 'laizhangtu.cache.stats',
  cacheClear: 'laizhangtu.cache.clear',
}

// 与后端 _BLOCKED 同一套规则的前端副本：只为尽早给出提示，
// 真正的拦截在 server_v4.py，绕过前端直接调接口同样会被拒绝。
const BLOCK_RE = /幼女|幼児|幼小|幼龄|稚女|稚児|萝莉|罗莉|正太|未成年|小学生|中学生|女童|男童|儿童|孩童|ロリ|ショタ|児童|女子高生|\bchild(?:ren)?\b|\bkids?\b|\bunderage\b|\bminors?\b|\bpreteen\b|\btoddler\b|\bjailbait\b|\bloli(?:con|s)?\b|\bshotacon\b|\bshota\b/i

const SIZE_OPTIONS = ['原图 original', '中等 regular', '小图 small']

function mount(container, ctx) {
  const App = {
    data() {
      return {
        tab: 'fetch', tag: '', r18: false, current: null, history: [],
        cfg: null, stats: null, info: null,
        err: '', msg: '', loading: false, coolLeft: 0, _timer: null,
        searchTag: '', searchNum: 8, searchItems: [], searchMeta: null,
        searching: false, picking: null, showThumbs: false,
      }
    },
    methods: {
      async loadBase() {
        try {
          const [c, hres, s, i] = await Promise.all([
            ctx.invoke(IFACE.configGet),
            ctx.invoke(IFACE.historyList),
            ctx.invoke(IFACE.cacheStats),
            ctx.invoke(IFACE.info),
          ])
          this.cfg = c || {}
          this.r18 = !!this.cfg.r18
          this.history = (hres && hres.history) || []
          this.stats = s || null
          this.info = i || null
        } catch (e) { this.err = (e && e.message) || String(e) }
      },
      async doFetch() {
        if (BLOCK_RE.test(this.tag)) {
          this.err = '标签包含不允许的内容（涉及未成年人的性化内容），已拒绝。'
          return
        }
        // 面板 invoke 默认只等 15s（internal/pluginx/http.go），图片代理实测很慢，
        // 所以按后端同一份 fetch_timeout 预算 +5s 余量显式放宽，避免面板先掐断。
        const budget = Number(this.cfg && this.cfg.fetch_timeout) || 20
        const timeoutMs = Math.round((budget + 5) * 1000)
        this.loading = true; this.err = ''; this.msg = ''
        try {
          const r = await ctx.invoke(IFACE.fetch, { tag: this.tag, r18: this.r18 }, { timeoutMs })
          this.current = (r && r.items && r.items[0]) || null
          if (this.current && this.current.degraded) this.msg = '原图下载较慢，已自动降级为小图。'
          this.loadBase()
          this.coolLeft = Number(this.cfg && this.cfg.cool_down) || 0
        } catch (e) { this.err = (e && e.message) || String(e) }
        this.loading = false
      },
      async doSearch() {
        if (BLOCK_RE.test(this.searchTag)) {
          this.err = '标签包含不允许的内容（涉及未成年人的性化内容），已拒绝。'
          return
        }
        // 搜索只发一次 API（不下载图片），预算封顶 20s；仍显式放宽面板默认 15s。
        const budget = Number(this.cfg && this.cfg.fetch_timeout) || 20
        const timeoutMs = Math.round((Math.min(budget, 20) + 5) * 1000)
        this.searching = true; this.err = ''; this.msg = ''
        try {
          const r = await ctx.invoke(IFACE.search, {
            tag: this.searchTag, num: Number(this.searchNum) || 8, r18: this.r18,
          }, { timeoutMs })
          this.searchMeta = r || null
          this.searchItems = (r && r.items) || []
          if (r && r.message) this.msg = r.message
          else if (!this.searchItems.length) this.msg = '没有找到符合条件的插画，换个标签试试。'
        } catch (e) { this.err = (e && e.message) || String(e) }
        this.searching = false
      },
      async doPick(id) {
        if (!id) return
        const budget = Number(this.cfg && this.cfg.fetch_timeout) || 20
        const timeoutMs = Math.round((budget + 5) * 1000)
        this.picking = id; this.err = ''; this.msg = ''
        try {
          const r = await ctx.invoke(IFACE.pick, { id }, { timeoutMs })
          this.current = (r && r.items && r.items[0]) || null
          this.tab = 'fetch'
          this.msg = '已从搜索结果取图'
          this.loadBase()
          this.coolLeft = Number(this.cfg && this.cfg.cool_down) || 0
        } catch (e) { this.err = (e && e.message) || String(e) }
        this.picking = null
      },
      async clearHistory() {
        try {
          await ctx.invoke(IFACE.historyClear)
          this.history = []; this.current = null
          this.msg = '历史已清空'
        } catch (e) { this.err = (e && e.message) || String(e) }
      },
      async saveCfg() {
        try {
          const r = await ctx.invoke(IFACE.configSave, Object.assign({}, this.cfg))
          this.cfg = (r && r.config) || this.cfg
          this.msg = '设置已保存'
          this.loadBase()
        } catch (e) { this.err = (e && e.message) || String(e) }
      },
      async clearCache() {
        if (!window.confirm('清空所有缓存图片与历史记录？此操作不可撤销。')) return
        try {
          const r = await ctx.invoke(IFACE.cacheClear)
          this.current = null; this.history = []
          this.msg = (r && r.message) || '缓存已清空'
          this.loadBase()
        } catch (e) { this.err = (e && e.message) || String(e) }
      },
      showItem(it) { this.current = it; this.tab = 'fetch' },
    },
    mounted() {
      this.loadBase()
      this._timer = window.setInterval(() => { if (this.coolLeft > 0) this.coolLeft-- }, 1000)
    },
    beforeUnmount() { if (this._timer) window.clearInterval(this._timer) },
    render() {
      const budgetSec = () => Number(this.cfg && this.cfg.fetch_timeout) || 20
      const tabBtn = (k, label) => h('button', {
        class: 'btn btn-sm' + (this.tab === k ? ' btn-primary' : ''),
        onClick: () => { this.tab = k; this.err = ''; this.msg = '' },
      }, label)

      const currentCard = () => {
        const it = this.current
        if (!it) return h('p', { class: 'hint' }, '还没有取图，输入标签（可留空随机）后点「来一张」。')
        const showInfo = !this.cfg || this.cfg.show_info !== false
        const meta = showInfo ? h('div', { class: 'faint', style: 'font-size:12px;line-height:1.7;margin-top:8px;' }, [
          h('div', null, '标题：' + (it.title || '-')),
          h('div', null, '作者：' + (it.author || '-') + '   PID：' + (it.pid || '-') + '   UID：' + (it.uid || '-')),
          h('div', null, '尺寸：' + (it.width || '?') + ' × ' + (it.height || '?') + '   规格：' + (it.size || '-')),
          h('div', null, '标签：' + (it.tags || []).join(' / ')),
          it.is_blurred ? h('div', { style: 'color:var(--danger,#c33);' }, '咦？怎么变得这么模糊了？不会是最近看多了吧…') : null,
          it.degraded ? h('div', { class: 'faint', style: 'font-size:11px;' }, '原图下载较慢，已自动降级为小图') : null,
        ]) : null
        return h('div', { class: 'card', style: 'padding:10px;' }, [
          h('img', { src: it.url, style: 'width:100%;max-height:62vh;object-fit:contain;display:block;background:rgba(127,127,127,.08);' }),
          meta,
        ])
      }

      const historyGrid = () => h('div', { class: 'card-grid', style: 'grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:10px;' },
        this.history.length
          ? this.history.map((it, idx) => h('div', {
              key: (it.pid || idx) + '-' + idx, class: 'card',
              style: 'padding:6px;cursor:pointer;', onClick: () => this.showItem(it),
            }, [
              h('img', { src: it.url, loading: 'lazy', style: 'width:100%;height:130px;object-fit:cover;display:block;' }),
              h('div', { style: 'font-size:11px;margin-top:4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;' }, it.title || ('PID ' + it.pid)),
            ]))
          : h('p', { class: 'hint' }, '暂无历史记录'))

      const sw = (k, label) => h('label', {
        style: 'display:flex;gap:6px;align-items:center;font-size:13px;margin-bottom:6px;',
      }, [
        h('input', { type: 'checkbox', checked: !!this.cfg[k],
          onChange: (e) => { this.cfg[k] = e.target.checked } }),
        label,
      ])
      const num = (k, label, width) => h('div', { style: 'margin:6px 0;font-size:13px;' }, [
        label + ' ',
        h('input', { class: 'input', style: 'width:' + (width || '80px') + ';', type: 'number',
          value: this.cfg[k], onInput: (e) => { this.cfg[k] = e.target.value } }),
      ])

      const settingsPanel = () => this.cfg ? h('div', { class: 'section' }, [
        h('div', { style: 'display:flex;flex-wrap:wrap;gap:6px 24px;' }, [
          h('div', null, [sw('show_info', '显示作品信息'), sw('exclude_ai', '排除 AI 作品'), sw('exclude_seen', '排除已见过')]),
          h('div', null, [sw('flip_h', '水平翻转'), sw('flip_v', '垂直翻转'), sw('r18', '允许 R18（仅成年人）')]),
        ]),
        h('div', { style: 'margin:8px 0;font-size:13px;' }, [
          '图片规格 ',
          h('select', { class: 'input', style: 'width:170px;', value: this.cfg.img_size,
            onChange: (e) => { this.cfg.img_size = Number(e.target.value) } },
            SIZE_OPTIONS.map((s, i) => h('option', { value: i }, s))),
          '  代理域名 ',
          h('input', { class: 'input', style: 'width:180px;', value: this.cfg.proxy,
            onInput: (e) => { this.cfg.proxy = e.target.value } }),
        ]),
        num('blur_chance', '随机模糊概率 %（0-100）'),
        num('cool_down', '冷却时间（秒，0 关闭）'),
        num('max_cache_mb', '缓存上限（MB，超出自动删最旧）'),
        num('fetch_timeout', '取图超时（秒，5-180）'),
        h('div', { class: 'faint', style: 'font-size:11px;line-height:1.6;margin:6px 0 10px;' },
          '实测图片代理较慢：小图约 30KB，原图约 1.5MB 可能要几十秒。默认走「小图 small」；' +
          '若选原图，建议把取图超时调到 60 秒以上，超时后会自动降级为小图。面板按此值放宽等待时间。'),
        h('button', { class: 'btn btn-primary', onClick: () => this.saveCfg() }, '保存设置'),
        this.stats ? h('div', { class: 'faint', style: 'font-size:12px;margin-top:12px;' }, [
          h('div', null, '缓存：' + this.stats.count + ' 张 / ' + this.stats.mb + ' MB（上限 ' + this.stats.limit_mb + ' MB）'),
          h('div', null, '目录：' + (this.stats.dir || '-')),
          h('button', { class: 'btn btn-sm btn-danger', style: 'margin-top:6px;', onClick: () => this.clearCache() }, '清空缓存与历史'),
        ]) : null,
      ]) : h('p', { class: 'hint' }, '配置加载中…')

      const searchPanel = () => h('div', null, [
        h('div', { class: 'flex', style: 'gap:6px;margin-bottom:8px;flex-wrap:wrap;align-items:center;' }, [
          h('input', { class: 'input', style: 'flex:1;min-width:200px;',
            placeholder: '按标签搜索（可留空随机）：A|B 或，A&B 与',
            value: this.searchTag, onInput: (e) => { this.searchTag = e.target.value },
            onKeyup: (e) => { if (e.key === 'Enter') this.doSearch() } }),
          h('select', { class: 'input', style: 'width:110px;', value: this.searchNum,
            onChange: (e) => { this.searchNum = Number(e.target.value) } },
            [5, 8, 10, 20].map((n) => h('option', { value: n }, n + ' 条'))),
          h('label', { style: 'display:flex;align-items:center;font-size:12px;gap:4px;' }, [
            h('input', { type: 'checkbox', checked: this.r18,
              onChange: (e) => { this.r18 = e.target.checked } }), 'R18',
          ]),
          h('button', { class: 'btn btn-primary', disabled: this.searching,
            onClick: () => this.doSearch() }, this.searching ? '搜索中…' : '开始搜索'),
          h('label', { style: 'display:flex;align-items:center;font-size:12px;gap:4px;' }, [
            h('input', { type: 'checkbox', checked: this.showThumbs,
              onChange: (e) => { this.showThumbs = e.target.checked } }), '显示缩略图',
          ]),
        ]),
        h('div', { class: 'faint', style: 'font-size:11px;line-height:1.6;margin-bottom:8px;' },
          '最多 20 条（API 上限）。搜索只返回元数据、不下载图片；缩略图由浏览器直连图片代理且默认关闭，' +
          '选中后点「取这张」才会下载并存入本地缓存。结果有效期 30 分钟，重启插件后需重新搜索。'),
        this.searchMeta ? h('div', { class: 'faint', style: 'font-size:12px;margin-bottom:8px;' },
          '标签「' + (this.searchMeta.tag || '随机') + '」 · 请求 ' + this.searchMeta.num +
          ' 条 / 返回 ' + this.searchMeta.total + ' 条 / 可用 ' + this.searchMeta.returned +
          ' 条 · 过滤 ' + this.searchMeta.filtered + ' 条 · ' + this.searchMeta.elapsed_ms + ' ms' +
          (this.searchMeta.skipped_seen ? ' · 跳过已见 ' + this.searchMeta.skipped_seen + ' 条' : '')) : null,
        this.searchItems.length
          ? h('div', { class: 'card-grid', style: 'grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px;' },
              this.searchItems.map((it, idx) => h('div', {
                key: it.id || idx, class: 'card', style: 'padding:10px;',
              }, [
                (this.showThumbs && it.thumb) ? h('img', {
                  src: it.thumb, loading: 'lazy',
                  style: 'width:100%;height:150px;object-fit:cover;display:block;margin-bottom:8px;background:rgba(127,127,127,.08);',
                  onError: (e) => { if (e && e.target) e.target.style.display = 'none' },
                }) : null,
                h('div', { style: 'font-size:13px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;' },
                  it.title || '(无标题)'),
                h('div', { class: 'faint', style: 'font-size:11px;line-height:1.7;margin-top:4px;' }, [
                  h('div', null, '作者：' + (it.author || '-') + '  PID：' + (it.pid || '-')),
                  h('div', null, '尺寸：' + (it.width || '?') + ' × ' + (it.height || '?') + '  规格：' + (it.size || '-')),
                  h('div', { style: 'word-break:break-all;' }, '标签：' + ((it.tags || []).slice(0, 6).join(' / ') || '-')),
                ]),
                h('button', { class: 'btn btn-sm btn-primary', style: 'margin-top:8px;',
                  disabled: this.picking === it.id, onClick: () => this.doPick(it.id) },
                  this.picking === it.id ? '取图中…' : '取这张'),
              ])))
          : h('p', { class: 'hint' },
              this.searchMeta && this.searchMeta.total === 0
                ? '没有找到符合条件的插画，换个标签试试。'
                : '输入标签后点「开始搜索」，结果会列在这里。'),
      ])

      return h('div', null, [
        h('div', { class: 'section-title' }, '来张图 · Lolicon 随机插画'),
        h('div', { class: 'flex', style: 'gap:6px;margin-bottom:8px;' }, [
          tabBtn('fetch', '取图'), tabBtn('search', '搜索'),
          tabBtn('history', '历史 (' + this.history.length + ')'), tabBtn('cfg', '设置'),
        ]),
        this.err ? h('p', { style: 'color:var(--danger,#c33);font-size:12px;' }, this.err) : null,
        this.msg ? h('p', { style: 'color:var(--ok,#2a8);font-size:12px;' }, this.msg) : null,

        this.tab === 'fetch' ? h('div', null, [
          h('div', { class: 'flex', style: 'gap:6px;margin-bottom:8px;flex-wrap:wrap;align-items:center;' }, [
            h('input', { class: 'input', style: 'flex:1;min-width:200px;',
              placeholder: '标签表达式，可留空随机：A|B 表示或，A&B 表示与',
              value: this.tag, onInput: (e) => { this.tag = e.target.value },
              onKeyup: (e) => { if (e.key === 'Enter') this.doFetch() } }),
            h('label', { style: 'display:flex;align-items:center;font-size:12px;gap:4px;' }, [
              h('input', { type: 'checkbox', checked: this.r18,
                onChange: (e) => { this.r18 = e.target.checked } }), 'R18',
            ]),
            h('button', { class: 'btn btn-primary', disabled: this.loading || this.coolLeft > 0,
              onClick: () => this.doFetch() },
              this.loading ? '取图中…(≤' + budgetSec() + 's)' : (this.coolLeft > 0 ? '冷却 ' + this.coolLeft + 's' : '来一张')),
            h('button', { class: 'btn btn-sm', onClick: () => this.doFetch() }, '换一张'),
          ]),
          currentCard(),
        ]) : null,

        this.tab === 'search' ? searchPanel() : null,

        this.tab === 'history' ? h('div', null, [
          h('button', { class: 'btn btn-sm btn-danger', style: 'margin-bottom:8px;', onClick: () => this.clearHistory() }, '清空历史'),
          historyGrid(),
        ]) : null,

        this.tab === 'cfg' ? settingsPanel() : null,

        h('div', { class: 'faint', style: 'font-size:11px;line-height:1.6;margin-top:14px;border-top:1px solid rgba(127,127,127,.2);padding-top:8px;' }, [
          h('div', null, '仅限成年人在本地个人环境使用；请遵守所在地法律法规，勿将获取的内容对外传播。图片来自第三方公开 API，插件不预置、不分发任何图片素材。'),
          h('div', null, '不接受涉及未成年人的性化标签，也会丢弃 API 返回中命中相同规则的作品。'),
          this.info ? h('div', null, this.info.label + ' v' + this.info.version + ' · ' + this.info.source) : null,
        ]),
      ])
    },
  }
  const vm = createApp(App)
  vm.mount(container)
  return () => vm.unmount()
}

export function register(g) {
  g.__rcPluginV4__ = g.__rcPluginV4__ || {}
  g.__rcPluginV4__[NAME] = { pages: [{ path: '', title: '来张图' }], mount }
}
if (typeof window !== 'undefined') register(window)
