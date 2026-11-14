// 构建 Vue 前端：esbuild 内联 Vue，输出 IIFE assets/plugin.js
const path = require('path')
const fs = require('fs')
const esbuild = require(path.join(__dirname, '..', '..', 'RainCough-Core', 'web', 'node_modules', 'esbuild'))
const vue = path.join(__dirname, '..', '..', 'RainCough-Core', 'web', 'node_modules', 'vue', 'dist', 'vue.esm-browser.prod.js')

esbuild.build({
  entryPoints: [path.join(__dirname, 'frontend', 'plugin.js')],
  outfile: path.join(__dirname, 'assets', 'plugin.js'),
  bundle: true,
  format: 'iife',
  target: 'es2020',
  minify: process.env.RC_NO_MINIFY !== '1',
  legalComments: 'none',
  plugins: [{
    name: 'vue-inline',
    setup(build) {
      build.onResolve({ filter: /^vue$/ }, () => ({ path: vue }))
    },
  }],
}).then(() => {
  const size = fs.statSync(path.join(__dirname, 'assets', 'plugin.js')).size
  console.log('built assets/plugin.js', size, 'bytes')
}).catch((e) => { console.error(e); process.exit(1) })
