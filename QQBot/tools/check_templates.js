#!/usr/bin/env node
// 构建前模板体检：把插件前端里所有 `template:` 字符串交给 Vue 编译器过一遍。
//
// ★ 为什么必须有这一步：esbuild 只做 JS 语法检查，模板是**字符串**，
//   里面的 <div v-else> 少了配对的 v-if 它完全看不见。Vue 是在运行时
//   （mount 那一刻）才编译模板的，于是产物能构建成功、node --check 也通过，
//   但面板里一打开就是空白页 —— 2026-11-07 的 1.4.0 就这么挂过一次：
//   概览页删掉了第一组计数器的 v-if，却把下边的 v-else 留着，
//   编译报 "v-else/v-else-if has no adjacent v-if or v-else-if"，
//   mount 抛异常 → 整页白屏（PluginView 只在 console 里打一行 warn）。
//
// 用法: node tools/check_templates.js [插件目录，默认本插件]

const fs = require('fs')
const path = require('path')

const SRC = process.argv[2] || path.join(__dirname, '..')
const CORE = path.resolve(SRC, '..', '..', 'RainCough-Core')
const { compile } = require(path.join(CORE, 'web', 'node_modules', '@vue', 'compiler-dom'))

function collect(dir, out) {
  for (const f of fs.readdirSync(dir)) {
    const p = path.join(dir, f)
    const st = fs.statSync(p)
    if (st.isDirectory()) collect(p, out)
    else if (f.endsWith('.js')) out.push(p)
  }
  return out
}

// 抽出 template: `...` 的内容（跳过转义字符，避免把 \` 当成结束）
function extractTemplates(src) {
  const out = []
  const re = /template\s*:\s*`/g
  let m
  while ((m = re.exec(src))) {
    let i = m.index + m[0].length
    let buf = ''
    while (i < src.length) {
      const c = src[i]
      if (c === '\\') { buf += src[i] + src[i + 1]; i += 2; continue }
      if (c === '`') break
      buf += c; i++
    }
    out.push({ text: buf, at: m.index })
  }
  return out
}

const root = path.join(SRC, 'frontend')
const files = fs.existsSync(root) ? collect(root, []) : []
let bad = 0
let total = 0
for (const f of files) {
  const src = fs.readFileSync(f, 'utf8')
  for (const t of extractTemplates(src)) {
    total++
    const errs = []
    try {
      compile(t.text, { onError: (e) => errs.push(e), onWarn: () => {} })
    } catch (e) {
      errs.push(e)
    }
    if (!errs.length) continue
    bad++
    const line = src.slice(0, t.at).split('\n').length
    console.log('!! %s:%d 的模板编译失败', path.relative(SRC, f), line)
    const lines = t.text.split('\n')
    for (const e of errs) {
      console.log('   [%s] %s', e.code, e.message)
      if (e.loc) {
        const ln = e.loc.start.line
        for (let k = Math.max(0, ln - 2); k < Math.min(lines.length, ln + 1); k++) {
          console.log('   %s %3d | %s', k === ln - 1 ? '>>' : '  ', k + 1, lines[k].slice(0, 160))
        }
      }
    }
  }
}
if (bad) {
  console.log('\n模板检查失败：%d/%d 个模板有语法错误（产物能构建成功，但面板打开会白屏）', bad, total)
  process.exit(1)
}
console.log('模板检查通过：%d 个模板', total)
