import fs from 'node:fs'
import fsp from 'node:fs/promises'
import path from 'node:path'
import { spawn } from 'node:child_process'
import type { Config } from './types.js'

const SECRET_HINTS = [
  'password', 'passwd', 'secret', 'token', 'apikey', 'api_key',
  'privatekey', 'presharedkey', 'access_key', 'authorization',
]

export function redact(text: string): string {
  if (!text) return text
  return text
    .split('\n')
    .map((line) => {
      const low = line.toLowerCase()
      if (SECRET_HINTS.some((h) => low.includes(h)) && /([=:])\s*\S+/.test(line)) {
        return line.replace(/([=:])\s*\S+.*/, '$1 ***')
      }
      return line
    })
    .join('\n')
}

function cap(text: string, n: number): string {
  if (text.length <= n) return text
  return text.slice(0, n) + `\n... [输出已截断, 共 ${text.length} 字符]`
}

function resolveIn(cfg: Config, p: string): string {
  const base = path.resolve(cfg.workspace)
  const abs = path.resolve(base, String(p || '.'))
  const rel = path.relative(base, abs)
  if (rel.startsWith('..') || path.isAbsolute(rel)) throw new Error('路径超出工作区: ' + p)
  return abs
}

function execShell(cfg: Config, command: string): Promise<{ code: number; stdout: string; stderr: string; timedout: boolean }> {
  const timeout = Math.max(1, cfg.shell_timeout || 30)
  const capOut = Math.max(1024, cfg.output_cap || 20000)
  const win = process.platform === 'win32'
  const argv = win ? ['cmd', '/c', command] : ['/bin/bash', '-lc', command]
  return new Promise((resolve) => {
    let child: ReturnType<typeof spawn>
    try {
      child = spawn(argv[0], argv.slice(1), { cwd: cfg.workspace, env: { ...process.env } })
    } catch (e: any) {
      resolve({ code: -1, stdout: '', stderr: e.message || String(e), timedout: false })
      return
    }
    let out = ''
    let err = ''
    let timedout = false
    const t = setTimeout(() => {
      timedout = true
      try { child.kill('SIGKILL') } catch { /* noop */ }
    }, timeout * 1000)
    if (child.stdout) {
      child.stdout.on('data', (d: Buffer) => {
        if (out.length < capOut * 2) out += d.toString('utf8')
      })
    }
    if (child.stderr) {
      child.stderr.on('data', (d: Buffer) => {
        if (err.length < 8192) err += d.toString('utf8')
      })
    }
    child.on('error', (e) => {
      clearTimeout(t)
      resolve({ code: -1, stdout: out, stderr: e.message, timedout })
    })
    child.on('close', (code) => {
      clearTimeout(t)
      resolve({ code: code ?? -1, stdout: out, stderr: err, timedout })
    })
  })
}

async function readFileTool(cfg: Config, args: any): Promise<string> {
  const abs = resolveIn(cfg, args.path)
  const st = await fsp.stat(abs)
  if (st.isDirectory()) throw new Error('是目录: ' + args.path)
  let lines = (await fsp.readFile(abs, 'utf-8')).split('\n')
  const o = Math.max(0, Number(args.offset) || 0)
  const lim = Number(args.limit) || lines.length
  const shown = lines.slice(o, o + lim).join('\n')
  const total = lines.length
  return `[文件: ${abs} 总行数: ${total} 已显示 ${o + 1}-${Math.min(total, o + lim)}]\n${cap(shown, cfg.output_cap || 20000)}`
}

async function writeFileTool(cfg: Config, args: any): Promise<string> {
  const abs = resolveIn(cfg, args.path)
  const content = String(args.content ?? '')
  await fsp.mkdir(path.dirname(abs), { recursive: true })
  await fsp.writeFile(abs, content, 'utf-8')
  return `已写入 ${abs} (${Buffer.byteLength(content)} 字节)`
}

async function editFileTool(cfg: Config, args: any): Promise<string> {
  const abs = resolveIn(cfg, args.path)
  const cur = await fsp.readFile(abs, 'utf-8')
  const oldS = String(args.old ?? '')
  const newS = String(args.new ?? '')
  const i = cur.indexOf(oldS)
  if (i < 0) throw new Error(`未在 ${abs} 中找到要替换的文本`)
  const next = cur.slice(0, i) + newS + cur.slice(i + oldS.length)
  await fsp.writeFile(abs, next, 'utf-8')
  return `已编辑 ${abs}`
}

async function listDirTool(cfg: Config, args: any): Promise<string> {
  const abs = resolveIn(cfg, args.path)
  const ents = await fsp.readdir(abs, { withFileTypes: true })
  const rows = ents.slice(0, 500).map((e) => {
    let size = 0
    if (e.isFile()) {
      try { size = fs.statSync(path.join(abs, e.name)).size } catch { /* noop */ }
    }
    return `${e.isDirectory() ? 'd' : 'f'} ${size}\t${e.name}`
  })
  return `[目录: ${abs} 共 ${ents.length} 项]\n` + rows.join('\n')
}

async function searchTool(cfg: Config, args: any): Promise<string> {
  const abs = resolveIn(cfg, args.path)
  const pat = String(args.pattern || '').toLowerCase()
  if (!pat) throw new Error('缺少搜索关键字 pattern')
  const out: string[] = []
  const maxFiles = 3000
  const maxHits = 60
  let count = 0
  async function walk(dir: string, depth: number) {
    if (out.length >= maxHits || count >= maxFiles || depth > 6) return
    let entries
    try { entries = await fsp.readdir(dir, { withFileTypes: true }) } catch { return }
    for (const e of entries) {
      if (out.length >= maxHits || count >= maxFiles) return
      if (e.name.startsWith('.')) continue
      const fp = path.join(dir, e.name)
      if (e.isDirectory()) {
        await walk(fp, depth + 1)
        continue
      }
      count++
      if (e.name.toLowerCase().includes(pat)) {
        out.push('[命中文件名] ' + path.relative(abs, fp))
        continue
      }
      try {
        const head = fs.readFileSync(fp, 'utf-8').slice(0, 8192).toLowerCase()
        if (head.includes(pat)) out.push(path.relative(abs, fp))
      } catch { /* noop */ }
    }
  }
  await walk(abs, 0)
  return out.length
    ? `[搜索: ${pat} in ${abs} 命中 ${out.length}]\n` + out.join('\n')
    : `未找到匹配 "${pat}"`
}

export interface ToolOutput { content: string }

export async function execTool(cfg: Config, name: string, args: any): Promise<ToolOutput> {
  switch (name) {
    case 'execute_shell': {
      const r = await execShell(cfg, String(args.command || ''))
      const header = `[exit ${r.code}${r.timedout ? ' 超时被终止' : ''}]`
      const parts: string[] = [header]
      const outC = cap(r.stdout, cfg.output_cap || 20000)
      const errC = cap(r.stderr, 4096)
      if (outC.trim()) parts.push(redact(outC))
      if (errC.trim()) parts.push('[stderr]\n' + redact(errC))
      return { content: parts.join('\n').trim() }
    }
    case 'read_file':
      return { content: await readFileTool(cfg, args) }
    case 'write_file':
      return { content: await writeFileTool(cfg, args) }
    case 'edit_file':
      return { content: await editFileTool(cfg, args) }
    case 'list_dir':
      return { content: await listDirTool(cfg, args) }
    case 'search':
      return { content: await searchTool(cfg, args) }
    default:
      throw new Error('未知工具: ' + name)
  }
}

export function buildToolDefs(): any[] {
  const s = (name: string, description: string, props: Record<string, any>, req: string[]) => ({
    type: 'function',
    function: { name, description, parameters: { type: 'object', properties: props, required: req } },
  })
  return [
    s(
      'execute_shell',
      '在服务器工作区内执行 bash 命令。用于构建、运行测试、安装依赖、查看状态、日志等。',
      { command: { type: 'string', description: '要执行的 bash 命令' } },
      ['command']
    ),
    s(
      'read_file',
      '读取文本文件内容, 可指定行范围。',
      {
        path: { type: 'string', description: '工作区内的路径' },
        offset: { type: 'number', description: '起始行(从 0 开始)' },
        limit: { type: 'number', description: '读取行数' },
      },
      ['path']
    ),
    s(
      'write_file',
      '写入文件(覆盖)。父目录不存在会自动创建。',
      { path: { type: 'string' }, content: { type: 'string', description: '文件完整内容' } },
      ['path', 'content']
    ),
    s(
      'edit_file',
      '在文件中做精确文本替换(替换首个匹配)。',
      {
        path: { type: 'string' },
        old: { type: 'string', description: '要替换的原文' },
        new: { type: 'string', description: '替换后的文本' },
      },
      ['path', 'old', 'new']
    ),
    s('list_dir', '列出目录内容。', { path: { type: 'string' } }, ['path']),
    s(
      'search',
      '在工作区中按关键字搜索文件名或文件内容。',
      { path: { type: 'string', description: '搜索起点目录' }, pattern: { type: 'string', description: '搜索关键字' } },
      ['path', 'pattern']
    ),
    s(
      'update_todo',
      '维护任务清单。action: add(新增, 需 text)/done(完成)/undo/remove/clear/replace(整体替换, 需 items)。',
      {
        action: { type: 'string', enum: ['add', 'done', 'undo', 'remove', 'clear', 'replace'] },
        text: { type: 'string', description: 'add 时的任务文本' },
        id: { type: 'string', description: 'done/undo/remove 时的任务 id' },
        items: {
          type: 'array',
          items: {
            type: 'object',
            properties: { text: { type: 'string' }, done: { type: 'boolean' } },
          },
        },
      },
      ['action']
    ),
  ]
}
