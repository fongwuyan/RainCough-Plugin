// 号池管理台 · RainCough 插件前端（原生 JS，无构建步骤）
const NAME = 'AccountPool'
const $ = (sel, root = document) => root.querySelector(sel)
const esc = (v) => String(v == null ? '' : v).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]))

function mount(container, ctx) {
  container.innerHTML = ''
  const root = document.createElement('div')
  root.className = 'page'
  root.innerHTML = `
    <div class="page-head"><div>
      <h1>号池管理台</h1>
      <p class="subtitle">账号 / API Key 池 · 路由 · 下游 Token · LAN OpenAI 兼容入口</p>
    </div><div class="flex" style="gap:8px;">
      <button class="btn btn-sm" data-act="refresh">刷新</button>
      <button class="btn btn-sm" data-act="restart">重启网关</button>
    </div></div>
    <div class="page-body">
      <div id="ap-notice" class="hint" style="min-height:20px;color:var(--danger);"></div>
      <div class="flex" style="gap:6px;flex-wrap:wrap;margin-bottom:12px;">
        <button class="btn btn-sm btn-primary" data-tab="overview">概览</button>
        <button class="btn btn-sm" data-tab="providers">Provider / 账号</button>
        <button class="btn btn-sm" data-tab="tokens">下游 Token</button>
        <button class="btn btn-sm" data-tab="settings">设置</button>
      </div>
      <div id="ap-body"></div>
    </div>`
  container.appendChild(root)

  let tab = 'overview'
  let cache = { status: null, providers: [], accounts: [], tokens: [], models: [] }

  const notice = (msg) => { $('#ap-notice', root).textContent = msg || '' }
  const call = (method, path, body) => ctx.invoke('accountpool.request', { method, path, body })

  async function load() {
    try {
      cache.status = await ctx.invoke('accountpool.status', {})
      const [p, a, t, m] = await Promise.all([
        call('GET', '/admin/v1/providers'), call('GET', '/admin/v1/accounts'),
        call('GET', '/admin/v1/tokens'), call('GET', '/admin/v1/models'),
      ])
      cache.providers = p.providers || []
      cache.accounts = a.accounts || []
      cache.tokens = t.tokens || []
      cache.models = m.models || []
      notice('')
    } catch (e) { notice((e && e.message) || String(e)) }
    render()
  }

  function render() {
    if (tab === 'overview') renderOverview()
    else if (tab === 'providers') renderProviders()
    else if (tab === 'tokens') renderTokens()
    else renderSettings()
  }

  function renderOverview() {
    const s = cache.status || {}
    const active = cache.accounts.filter((a) => a.enabled && a.status !== 'disabled' && !(a.cooldown_until > Date.now() / 1000)).length
    $('#ap-body', root).innerHTML = `
      <div class="grid" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;">
        ${card('网关', s.ok ? '运行中' : '未启动')}${card('版本', s.version || '—')}
        ${card('Provider', cache.providers.length)}${card('账号', cache.accounts.length + ' / 可用 ' + active)}
        ${card('下游 Token', cache.tokens.length)}${card('模型', cache.models.length)}
      </div>
      <div class="section-title" style="margin-top:16px;">LAN API</div>
      <div class="hint">Base URL：<code>${esc(s.lan_addr || '—')}</code> · 默认仅回环，设置中可显式开启局域网</div>
      <div class="section-title" style="margin-top:16px;">模型</div>
      <div class="hint">${cache.models.length ? cache.models.map((m) => esc(m.id)).join(' · ') : '暂无模型，请添加 Provider 并同步模型'}</div>`
  }

  function card(label, value) {
    return `<div class="card" style="padding:12px;"><div class="hint">${esc(label)}</div><div style="font-size:22px;font-weight:700;margin-top:4px;">${esc(value)}</div></div>`
  }

  function renderProviders() {
    const opts = cache.providers.map((p) => `<option value="${esc(p.id)}">${esc(p.name)} (${esc(p.type)})</option>`).join('')
    const rows = cache.providers.map((p) => `<tr><td>${esc(p.name)}</td><td>${esc(p.type)}</td><td class="mono">${esc(p.base_url)}</td><td>${p.has_key ? '已配置' : '未配置'}</td><td>${p.enabled ? '启用' : '停用'}</td><td><button class="btn btn-sm" data-sync="${esc(p.id)}">同步模型</button></td></tr>`).join('')
    const arows = cache.accounts.map((a) => `<tr><td>${esc(a.label)}</td><td class="mono">${esc(a.provider_id)}</td><td>${esc(a.status)}</td><td>${a.weight}/${a.priority}</td><td>${a.enabled ? '启用' : '停用'}</td><td>${esc(a.last_error || '')}</td></tr>`).join('')
    $('#ap-body', root).innerHTML = `
      <div class="section-title">Provider</div>
      <div style="overflow:auto;"><table class="table"><thead><tr><th>名称</th><th>类型</th><th>Base URL</th><th>Key</th><th>状态</th><th></th></tr></thead><tbody>${rows || '<tr><td colspan="6" class="hint">暂无 Provider</td></tr>'}</tbody></table></div>
      <div class="card" style="padding:12px;margin-top:10px;">
        <div class="section-title">新增 / 更新 Provider</div>
        <div class="flex" style="gap:8px;flex-wrap:wrap;">
          <input class="input" id="p-name" placeholder="名称" style="width:140px;">
          <select class="input" id="p-type" style="width:150px;">${['openai','azure','anthropic','gemini','deepseek','zhipu','moonshot','qwen','ollama','vllm','custom'].map((x) => `<option>${x}</option>`).join('')}</select>
          <input class="input" id="p-base" placeholder="Base URL，如 https://api.openai.com/v1" style="flex:1;min-width:240px;">
          <input class="input" id="p-key" placeholder="API Key（留空不更新）" style="width:220px;">
          <input class="input" id="p-models" placeholder="模型，逗号分隔" style="width:220px;">
          <button class="btn btn-primary" data-act="add-provider">保存 Provider</button>
        </div>
      </div>
      <div class="section-title" style="margin-top:16px;">账号</div>
      <div style="overflow:auto;"><table class="table"><thead><tr><th>标签</th><th>Provider</th><th>状态</th><th>权重/优先级</th><th>启用</th><th>错误</th></tr></thead><tbody>${arows || '<tr><td colspan="6" class="hint">暂无账号</td></tr>'}</tbody></table></div>
      <div class="card" style="padding:12px;margin-top:10px;">
        <div class="section-title">新增账号 / Key</div>
        <div class="flex" style="gap:8px;flex-wrap:wrap;">
          <select class="input" id="a-provider" style="width:200px;">${opts || '<option value="">先添加 Provider</option>'}</select>
          <input class="input" id="a-label" placeholder="标签" style="width:140px;">
          <input class="input" id="a-key" placeholder="API Key" style="flex:1;min-width:220px;">
          <input class="input" id="a-weight" placeholder="权重" value="1" style="width:70px;">
          <input class="input" id="a-priority" placeholder="优先级" value="0" style="width:80px;">
          <button class="btn btn-primary" data-act="add-account">保存账号</button>
        </div>
      </div>`
  }

  function renderTokens() {
    const rows = cache.tokens.map((t) => `<tr><td>${esc(t.name)}</td><td>${t.rpm || '不限'}</td><td>${t.daily_quota || '不限'}</td><td>${t.used_count}/${t.used_day || '—'}</td><td>${t.enabled ? '启用' : '已吊销'}</td><td><button class="btn btn-sm" data-revoke="${esc(t.id)}">吊销</button></td></tr>`).join('')
    $('#ap-body', root).innerHTML = `
      <div class="section-title">下游 Token</div>
      <div style="overflow:auto;"><table class="table"><thead><tr><th>名称</th><th>RPM</th><th>日额度</th><th>今日用量</th><th>状态</th><th></th></tr></thead><tbody>${rows || '<tr><td colspan="6" class="hint">暂无 Token</td></tr>'}</tbody></table></div>
      <div class="card" style="padding:12px;margin-top:10px;">
        <div class="flex" style="gap:8px;flex-wrap:wrap;">
          <input class="input" id="t-name" placeholder="Token 名称" style="width:180px;">
          <input class="input" id="t-rpm" placeholder="RPM（0=不限）" style="width:130px;">
          <input class="input" id="t-quota" placeholder="日请求额度（0=不限）" style="width:180px;">
          <button class="btn btn-primary" data-act="add-token">创建 Token</button>
        </div>
        <div id="ap-new-token" class="hint" style="margin-top:8px;"></div>
      </div>`
  }

  function renderSettings() {
    const s = cache.status || {}
    $('#ap-body', root).innerHTML = `
      <div class="section-title">LAN API</div>
      <div class="card" style="padding:12px;">
        <div class="hint">默认只监听回环。开启局域网会允许同网段设备使用下游 Token 访问。</div>
        <div class="flex" style="gap:8px;margin-top:8px;flex-wrap:wrap;">
          <input class="input" id="s-lan" value="${esc(s.lan_addr || '127.0.0.1:18900')}" style="width:220px;">
          <label class="hint"><input type="checkbox" id="s-enable"> 允许局域网访问</label>
          <button class="btn btn-primary" data-act="save-lan">保存并重启</button>
        </div>
      </div>
      <div class="section-title" style="margin-top:16px;">网关日志</div>
      <pre id="ap-log" class="hint" style="max-height:260px;overflow:auto;background:var(--bg-raised);padding:10px;border-radius:6px;"></pre>
      <button class="btn btn-sm" data-act="load-log">读取日志</button>`
  }

  async function addProvider() {
    try {
      const models = $('#p-models', root).value.split(',').map((x) => x.trim()).filter(Boolean)
      await call('POST', '/admin/v1/providers', {
        name: $('#p-name', root).value.trim(), type: $('#p-type', root).value,
        base_url: $('#p-base', root).value.trim(), api_key: $('#p-key', root).value.trim(), models,
      })
      await load()
    } catch (e) { notice((e && e.message) || String(e)) }
  }

  async function addAccount() {
    try {
      await call('POST', '/admin/v1/accounts', {
        provider_id: $('#a-provider', root).value, label: $('#a-label', root).value.trim(),
        api_key: $('#a-key', root).value.trim(),
        weight: Number($('#a-weight', root).value) || 1,
        priority: Number($('#a-priority', root).value) || 0,
      })
      await load()
    } catch (e) { notice((e && e.message) || String(e)) }
  }

  async function addToken() {
    try {
      const d = await call('POST', '/admin/v1/tokens', {
        name: $('#t-name', root).value.trim(), rpm: Number($('#t-rpm', root).value) || 0,
        daily_quota: Number($('#t-quota', root).value) || 0,
      })
      $('#ap-new-token', root).innerHTML = '新 Token（只显示一次）：<code>' + esc(d.token) + '</code>'
      await load()
    } catch (e) { notice((e && e.message) || String(e)) }
  }

  async function saveLan() {
    try {
      const enabled = $('#s-enable', root).checked
      let addr = $('#s-lan', root).value.trim()
      if (enabled && !addr) addr = '0.0.0.0:18900'
      await ctx.invoke('accountpool.settings.save', { lan_enabled: enabled, lan_addr: addr })
      await ctx.invoke('accountpool.gateway.restart', {})
      await load()
      notice('LAN 设置已保存并重启')
    } catch (e) { notice((e && e.message) || String(e)) }
  }

  root.addEventListener('click', async (ev) => {
    const t = ev.target.closest('button')
    if (!t) return
    if (t.dataset.tab) { tab = t.dataset.tab; render(); return }
    if (t.dataset.act === 'refresh') return load()
    if (t.dataset.act === 'restart') { try { await ctx.invoke('accountpool.gateway.restart', {}); await load() } catch (e) { notice((e && e.message) || String(e)) } return }
    if (t.dataset.act === 'add-provider') return addProvider()
    if (t.dataset.act === 'add-account') return addAccount()
    if (t.dataset.act === 'add-token') return addToken()
    if (t.dataset.act === 'save-lan') return saveLan()
    if (t.dataset.act === 'load-log') { try { const d = await ctx.invoke('accountpool.gateway.log', {}); $('#ap-log', root).textContent = d.log || '（空）' } catch (e) { notice(String(e)) } return }
    if (t.dataset.sync) { try { await call('POST', '/admin/v1/providers/' + encodeURIComponent(t.dataset.sync) + '/sync'); await load() } catch (e) { notice((e && e.message) || String(e)) } return }
    if (t.dataset.revoke) { try { await call('DELETE', '/admin/v1/tokens/' + encodeURIComponent(t.dataset.revoke)); await load() } catch (e) { notice((e && e.message) || String(e)) } return }
  })

  load()
  return () => { container.innerHTML = '' }
}

export function register(g) {
  g.__rcPluginV4__ = g.__rcPluginV4__ || {}
  g.__rcPluginV4__[NAME] = { pages: [{ path: '', title: '号池管理台' }], mount }
}
if (typeof window !== 'undefined') register(window)
