// demo 插件前端(接口库 v4): Vue3 展示层, 只调用 ctx.invoke, 零业务逻辑。
// 产物由 tools/build-plugin-frontend.js 构建为 assets/plugin.js(含 Vue 运行时)。
import { createApp, ref } from 'vue'

const NAME = 'demo'

let instance = null

function mount(el, ctx) {
  const result = ref('')
  const loading = ref(false)

  async function call(iface, params) {
    loading.value = true
    try {
      const r = await ctx.invoke(iface, params || {})
      result.value = JSON.stringify(r, null, 2)
    } catch (e) {
      result.value = 'ERR: ' + ((e && e.message) || e)
    } finally {
      loading.value = false
    }
  }

  instance = createApp({
    setup() {
      return { result, loading, call, plugin: ctx.plugin }
    },
    template: `
      <div class="rc-demo">
        <h3>{{ plugin.label }} <span class="faint">接口库 v4 演示</span></h3>
        <p>插件 <b>{{ plugin.name }}</b> v{{ plugin.version }} —— Vue3 只展示, 逻辑在后端</p>
        <div style="display:flex;gap:8px;flex-wrap:wrap">
          <button :disabled="loading" @click="call('demo.ping')">demo.ping</button>
          <button :disabled="loading" @click="call('demo.echo', {msg:'你好'})">demo.echo</button>
          <button :disabled="loading" @click="call('demo.cross', {a:1})">demo.cross(跨接口)</button>
        </div>
        <pre class="rc-demo-out">{{ result || '未调用' }}</pre>
      </div>
    `,
  })
  instance.mount(el)
  return () => instance.unmount()
}

export function register(g) {
  g.__rcPluginV4__ = g.__rcPluginV4__ || {}
  g.__rcPluginV4__[NAME] = { pages: [{ path: '', title: '接口演示' }], mount }
}