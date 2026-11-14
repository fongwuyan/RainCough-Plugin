// 号池管理台 · RainCough 插件前端（Vue 3，esbuild 内联打包）
import { createApp } from 'vue'

const NAME = 'AccountPool'
const TYPES = ['openai', 'azure', 'anthropic', 'gemini', 'deepseek', 'zhipu', 'moonshot', 'qwen', 'ollama', 'vllm', 'custom']

const TEMPLATE = `
<div class="page">
  <div class="page-head"><div>
    <h1>号池管理台</h1>
    <p class="subtitle">账号 / API Key 池 · 路由 · 下游 Token · LAN OpenAI / Anthropic / Gemini 入口</p>
  </div><div class="flex" style="gap:8px;">
    <button class="btn btn-sm" @click="load">刷新</button>
    <button class="btn btn-sm" @click="restartGateway">重启网关</button>
  </div></div>
  <div class="page-body">
    <div v-if="notice" class="hint" style="color:var(--danger);min-height:20px;">{{ notice }}</div>
    <div class="flex" style="gap:6px;flex-wrap:wrap;margin-bottom:12px;">
      <button v-for="x in tabs" :key="x.id" class="btn btn-sm" :class="tab===x.id?'btn-primary':''" @click="tab=x.id">{{ x.label }}</button>
    </div>

    <template v-if="tab==='overview'">
      <div class="grid" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;">
        <div class="card" style="padding:12px;" v-for="c in cards" :key="c[0]"><div class="hint">{{ c[0] }}</div><div style="font-size:22px;font-weight:700;margin-top:4px;">{{ c[1] }}</div></div>
      </div>
      <div class="section-title" style="margin-top:16px;">LAN API</div>
      <div class="hint">Base URL：<code>{{ status.lan_addr || '—' }}</code> · 默认仅回环，设置中可显式开启局域网</div>
      <div class="section-title" style="margin-top:16px;">模型</div>
      <div class="hint">{{ models.length ? models.map(m=>m.id).join(' · ') : '暂无模型，请添加 Provider 并同步模型' }}</div>
    </template>

    <template v-if="tab==='providers'">
      <div class="section-title">Provider</div>
      <div style="overflow:auto;"><table class="table"><thead><tr><th>名称</th><th>类型</th><th>Base URL</th><th>Key</th><th>状态</th><th></th></tr></thead><tbody>
        <tr v-for="p in providers" :key="p.id"><td>{{ p.name }}</td><td>{{ p.type }}</td><td class="mono">{{ p.base_url }}</td><td>{{ p.has_key ? '已配置' : '未配置' }}</td><td>{{ p.enabled ? '启用' : '停用' }}</td><td><button class="btn btn-sm" @click="syncProvider(p.id)">同步模型</button></td></tr>
        <tr v-if="!providers.length"><td colspan="6" class="hint">暂无 Provider</td></tr>
      </tbody></table></div>
      <div class="card" style="padding:12px;margin-top:10px;">
        <div class="section-title">新增 / 更新 Provider</div>
        <div class="flex" style="gap:8px;flex-wrap:wrap;">
          <input class="input" v-model="pf.name" placeholder="名称" style="width:140px;">
          <select class="input" v-model="pf.type" style="width:150px;"><option v-for="t in types" :key="t">{{ t }}</option></select>
          <input class="input" v-model="pf.base_url" placeholder="Base URL，如 https://api.openai.com/v1" style="flex:1;min-width:240px;">
          <input class="input" v-model="pf.api_key" placeholder="API Key（留空不更新）" style="width:220px;">
          <input class="input" v-model="pf.models" placeholder="模型，逗号分隔" style="width:220px;">
          <button class="btn btn-primary" @click="addProvider">保存 Provider</button>
        </div>
      </div>
      <div class="section-title" style="margin-top:16px;">账号</div>
      <div style="overflow:auto;"><table class="table"><thead><tr><th>标签</th><th>Provider</th><th>状态</th><th>权重/优先级</th><th>启用</th><th>错误</th></tr></thead><tbody>
        <tr v-for="a in accounts" :key="a.id"><td>{{ a.label }}</td><td class="mono">{{ a.provider_id }}</td><td>{{ a.status }}</td><td>{{ a.weight }}/{{ a.priority }}</td><td>{{ a.enabled ? '启用' : '停用' }}</td><td>{{ a.last_error }}</td></tr>
        <tr v-if="!accounts.length"><td colspan="6" class="hint">暂无账号</td></tr>
      </tbody></table></div>
      <div class="card" style="padding:12px;margin-top:10px;">
        <div class="section-title">新增账号 / Key</div>
        <div class="flex" style="gap:8px;flex-wrap:wrap;">
          <select class="input" v-model="af.provider_id" style="width:200px;"><option value="">选择 Provider</option><option v-for="p in providers" :key="p.id" :value="p.id">{{ p.name }} ({{ p.type }})</option></select>
          <input class="input" v-model="af.label" placeholder="标签" style="width:140px;">
          <input class="input" v-model="af.api_key" placeholder="API Key" style="flex:1;min-width:220px;">
          <input class="input" v-model.number="af.weight" placeholder="权重" style="width:70px;">
          <input class="input" v-model.number="af.priority" placeholder="优先级" style="width:80px;">
          <button class="btn btn-primary" @click="addAccount">保存账号</button>
        </div>
      </div>
    </template>

    <template v-if="tab==='tokens'">
      <div class="section-title">下游 Token</div>
      <div style="overflow:auto;"><table class="table"><thead><tr><th>名称</th><th>RPM</th><th>日额度</th><th>今日用量</th><th>状态</th><th></th></tr></thead><tbody>
        <tr v-for="t in tokens" :key="t.id"><td>{{ t.name }}</td><td>{{ t.rpm || '不限' }}</td><td>{{ t.daily_quota || '不限' }}</td><td>{{ t.used_count }}/{{ t.used_day || '—' }}</td><td>{{ t.enabled ? '启用' : '已吊销' }}</td><td><button class="btn btn-sm" @click="revokeToken(t.id)">吊销</button></td></tr>
        <tr v-if="!tokens.length"><td colspan="6" class="hint">暂无 Token</td></tr>
      </tbody></table></div>
      <div class="card" style="padding:12px;margin-top:10px;">
        <div class="flex" style="gap:8px;flex-wrap:wrap;">
          <input class="input" v-model="tf.name" placeholder="Token 名称" style="width:180px;">
          <input class="input" v-model.number="tf.rpm" placeholder="RPM（0=不限）" style="width:130px;">
          <input class="input" v-model.number="tf.daily_quota" placeholder="日请求额度（0=不限）" style="width:180px;">
          <button class="btn btn-primary" @click="addToken">创建 Token</button>
        </div>
        <div v-if="newToken" class="hint" style="margin-top:8px;">新 Token（只显示一次）：<code>{{ newToken }}</code></div>
      </div>
    </template>

    <template v-if="tab==='settings'">
      <div class="section-title">LAN API</div>
      <div class="card" style="padding:12px;">
        <div class="hint">默认只监听回环。开启局域网会允许同网段设备使用下游 Token 访问。</div>
        <div class="flex" style="gap:8px;margin-top:8px;flex-wrap:wrap;">
          <input class="input" v-model="lanAddr" style="width:220px;">
          <label class="hint"><input type="checkbox" v-model="lanEnabled"> 允许局域网访问</label>
          <button class="btn btn-primary" @click="saveLan">保存并重启</button>
        </div>
      </div>
      <div class="section-title" style="margin-top:16px;">网关日志</div>
      <pre class="hint" style="max-height:260px;overflow:auto;background:var(--bg-raised);padding:10px;border-radius:6px;">{{ log || '（未读取）' }}</pre>
      <button class="btn btn-sm" @click="loadLog">读取日志</button>
    </template>
  </div>
</div>`

function mount(container, ctx) {
  const call = (method, path, body) => ctx.invoke('accountpool.request', { method, path, body })
  const app = createApp({
    template: TEMPLATE,
    data() {
      return {
        tabs: [{ id: 'overview', label: '概览' }, { id: 'providers', label: 'Provider / 账号' }, { id: 'tokens', label: '下游 Token' }, { id: 'settings', label: '设置' }],
        tab: 'overview', status: {}, providers: [], accounts: [], tokens: [], models: [],
        notice: '', newToken: '', log: '', lanAddr: '127.0.0.1:18900', lanEnabled: false,
        types: TYPES,
        pf: { name: '', type: 'openai', base_url: '', api_key: '', models: '' },
        af: { provider_id: '', label: '', api_key: '', weight: 1, priority: 0 },
        tf: { name: '', rpm: 0, daily_quota: 0 },
      }
    },
    computed: {
      cards() {
        const s = this.status || {}
        const active = this.accounts.filter(a => a.enabled && a.status !== 'disabled' && !(a.cooldown_until > Date.now() / 1000)).length
        return [['网关', s.ok ? '运行中' : '未启动'], ['版本', s.version || '—'], ['Provider', this.providers.length], ['账号', this.accounts.length + ' / 可用 ' + active], ['下游 Token', this.tokens.length], ['模型', this.models.length]]
      },
    },
    mounted() { this.load() },
    methods: {
      async load() {
        this.notice = ''
        try {
          this.status = await ctx.invoke('accountpool.status', {}) || {}
          this.lanAddr = this.status.lan_addr || this.lanAddr
          this.lanEnabled = !!this.status.lan_enabled
          const [p, a, t, m] = await Promise.all([
            call('GET', '/admin/v1/providers'), call('GET', '/admin/v1/accounts'),
            call('GET', '/admin/v1/tokens'), call('GET', '/admin/v1/models'),
          ])
          this.providers = p.providers || []
          this.accounts = a.accounts || []
          this.tokens = t.tokens || []
          this.models = m.models || []
        } catch (e) { this.notice = (e && e.message) || String(e) }
      },
      async addProvider() {
        try {
          await call('POST', '/admin/v1/providers', {
            name: this.pf.name.trim(), type: this.pf.type, base_url: this.pf.base_url.trim(),
            api_key: this.pf.api_key.trim(), models: this.pf.models.split(',').map(x => x.trim()).filter(Boolean),
          })
          this.pf = { name: '', type: 'openai', base_url: '', api_key: '', models: '' }
          await this.load()
        } catch (e) { this.notice = (e && e.message) || String(e) }
      },
      async addAccount() {
        try {
          await call('POST', '/admin/v1/accounts', {
            provider_id: this.af.provider_id, label: this.af.label.trim(), api_key: this.af.api_key.trim(),
            weight: this.af.weight || 1, priority: this.af.priority || 0,
          })
          this.af = { provider_id: '', label: '', api_key: '', weight: 1, priority: 0 }
          await this.load()
        } catch (e) { this.notice = (e && e.message) || String(e) }
      },
      async addToken() {
        try {
          const d = await call('POST', '/admin/v1/tokens', { name: this.tf.name.trim(), rpm: this.tf.rpm || 0, daily_quota: this.tf.daily_quota || 0 })
          this.newToken = d.token || ''
          this.tf = { name: '', rpm: 0, daily_quota: 0 }
          await this.load()
        } catch (e) { this.notice = (e && e.message) || String(e) }
      },
      async revokeToken(id) {
        try { await call('DELETE', '/admin/v1/tokens/' + encodeURIComponent(id)); await this.load() }
        catch (e) { this.notice = (e && e.message) || String(e) }
      },
      async syncProvider(id) {
        try { await call('POST', '/admin/v1/providers/' + encodeURIComponent(id) + '/sync'); await this.load() }
        catch (e) { this.notice = (e && e.message) || String(e) }
      },
      async saveLan() {
        try {
          await ctx.invoke('accountpool.settings.save', { lan_enabled: this.lanEnabled, lan_addr: this.lanAddr })
          await ctx.invoke('accountpool.gateway.restart', {})
          await this.load()
          this.notice = 'LAN 设置已保存并重启'
        } catch (e) { this.notice = (e && e.message) || String(e) }
      },
      async restartGateway() {
        try { await ctx.invoke('accountpool.gateway.restart', {}); await this.load() }
        catch (e) { this.notice = (e && e.message) || String(e) }
      },
      async loadLog() {
        try { this.log = (await ctx.invoke('accountpool.gateway.log', {})).log || '（空）' }
        catch (e) { this.notice = (e && e.message) || String(e) }
      },
    },
  })
  app.mount(container)
  return () => app.unmount()
}

export function register(g) {
  g.__rcPluginV4__ = g.__rcPluginV4__ || {}
  g.__rcPluginV4__[NAME] = { pages: [{ path: '', title: '号池管理台' }], mount }
}
if (typeof window !== 'undefined') register(window)
