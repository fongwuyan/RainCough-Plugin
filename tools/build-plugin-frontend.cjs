// 构建插件前端产物：frontend/plugin.js -> assets/plugin.js（IIFE，内联 Vue）
//
// 用法（在 RainCough-Plugin 仓库根目录）：
//   node tools/build-plugin-frontend.cjs laizhangtu
//   RC_CORE_DIR=/path/to/RainCough-Core node tools/build-plugin-frontend.cjs laizhangtu QQBot
//   RC_VUE_DEV=1 RC_NO_MINIFY=1 node tools/build-plugin-frontend.cjs laizhangtu  # 调试
//
// 与面板仓库 tools/build-plugin-frontend.js 行为一致，只是把插件目录指向本仓库。
// Vue 与 esbuild 复用面板仓库 web/node_modules，插件仓库无需再装前端依赖。
const fs = require('fs')
const path = require('path')

const ROOT = path.resolve(__dirname, '..')
const CORE = process.env.RC_CORE_DIR || path.resolve(ROOT, '..', 'RainCough-Core')
const MODULES = path.join(CORE, 'web', 'node_modules')
const esbuild = require(path.join(MODULES, 'esbuild'))
const VUE_ESM = process.env.RC_VUE_DEV === '1'
  ? path.join(MODULES, 'vue', 'dist', 'vue.esm-browser.js')
  : path.join(MODULES, 'vue', 'dist', 'vue.esm-browser.prod.js')

async function buildPlugin(name) {
  const dir = path.join(ROOT, name)
  const entry = path.join(dir, 'frontend', 'plugin.js')
  if (!fs.existsSync(entry)) {
    console.log(`[skip] ${name}: 无 frontend/plugin.js`)
    return false
  }
  const outFile = path.join(dir, 'assets', 'plugin.js')
  fs.mkdirSync(path.dirname(outFile), { recursive: true })
  try {
    await esbuild.build({
      entryPoints: [entry],
      outfile: outFile,
      bundle: true,
      format: 'iife',
      plugins: [{
        name: 'vue-inline',
        setup(build) {
          build.onResolve({ filter: /^vue$/ }, () => ({ path: VUE_ESM }))
        },
      }],
      target: 'es2020',
      minify: process.env.RC_NO_MINIFY !== '1',
      legalComments: 'none',
    })
    const kb = (fs.statSync(outFile).size / 1024).toFixed(1)
    console.log(`[ok]   ${name}: assets/plugin.js (${kb} KB, vue=${VUE_ESM.includes('.prod.') ? 'prod' : 'dev'})`)
    return true
  } catch (e) {
    console.error(`[fail] ${name}:`, e.message)
    return false
  }
}

async function main() {
  const names = process.argv.slice(2)
  if (!names.length) {
    const available = fs.readdirSync(ROOT)
      .filter((d) => fs.existsSync(path.join(ROOT, d, 'frontend', 'plugin.js')))
    console.log('用法: node tools/build-plugin-frontend.cjs <插件名...>')
    console.log('可构建:', available.join(', ') || '(无)')
    process.exit(1)
  }
  let ok = 0
  for (const n of names) if (await buildPlugin(n)) ok++
  console.log(`\n构建完成: ${ok}/${names.length}`)
  if (ok !== names.length) process.exit(1)
}

main()
