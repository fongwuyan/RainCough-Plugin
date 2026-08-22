#!/usr/bin/env node
import http from 'node:http'
import fs from 'node:fs'
import path from 'node:path'
import { buildSystemPrompt, sanitizeSkills } from './skills.js'
import { streamChat } from './llm.js'
import { buildToolDefs, execTool, execSkillByName, redact } from './tools.js'
import type {
  Config, SessionState, Message, Todo, PendingTool, Skill, AssistantMsg, ToolCallArg,
} from './types.js'

const VERSION = '0.1.0'

function argVal(name: string, def: string): string {
  const i = process.argv.indexOf(name)
  return i >= 0 && process.argv[i + 1] ? process.argv[i + 1] : def
}
const PORT = parseInt(argVal('--port', process.env.RC_AGENT_PORT || '8765'), 10)
const DATA_DIR = path.resolve(argVal('--data', process.env.RC_DATA || path.join(process.cwd(), 'data')))
const SECRET = argVal('--secret', process.env.RC_SECRET || '')

const SESS_DIR = path.join(DATA_DIR, 'sessions')
const MEMORY_PATH = path.join(DATA_DIR, 'memory.md')
fs.mkdirSync(SESS_DIR, { recursive: true })

const sessions = new Map<string, SessionState>()

function saveSession(ss: SessionState) {
  const copy: any = { ...ss }
  delete copy._busy
  delete copy._cancel
  try {
    fs.writeFileSync(path.join(SESS_DIR, ss.id + '.json'), JSON.stringify(copy, null, 2))
  } catch (e: any) {
    console.error('[save]', ss.id, e && e.message)
  }
}

function loadSession(id: string): SessionState | null {
  const p = path.join(SESS_DIR, id + '.json')
  if (!fs.existsSync(p)) return null
  try {
    const j = JSON.parse(fs.readFileSync(p, 'utf-8'))
    return Object.assign({ _busy: false, _cancel: false }, j)
  } catch {
    return null
  }
}

function getSession(id: string): SessionState {
  let ss = sessions.get(id) || loadSession(id)
  if (!ss) {
    ss = {
      id, title: '新会话', created: Date.now(), updated: Date.now(),
      messages: [], todos: [], pending: null, active_skills: [], model: null, workspace: '',
      _busy: false, _cancel: false,
    }
  }
  sessions.set(id, ss)
  return ss
}

function sanitizeConfig(raw: any): Config {
  const approve = ['auto', 'confirm', 'whitelist'].includes(raw && raw.approve_mode)
    ? raw.approve_mode
    : 'confirm'
  const c: Config = {
    api_base: String((raw && raw.api_base) || 'https://opencode.ai/zen/v1').replace(/\/+$/, ''),
    api_key: String((raw && raw.api_key) || ''),
    model: String((raw && raw.model) || ''),
    workspace: path.resolve(String((raw && raw.workspace) || path.join(DATA_DIR, 'workspace'))),
    approve_mode: approve,
    agent_mode: (raw && raw.agent_mode) === 'plan' ? 'plan' : 'build',
    whitelist: Array.isArray(raw && raw.whitelist) ? raw.whitelist.map(String).filter(Boolean) : [],
    shell_timeout: Math.max(1, Number((raw && raw.shell_timeout) || 30)),
    output_cap: Math.max(1024, Number((raw && raw.output_cap) || 20000)),
    max_tool_steps: Math.max(1, Number((raw && raw.max_tool_steps) || 40)),
    memory_path: String((raw && raw.memory_path) || MEMORY_PATH),
    provider: String((raw && raw.provider) || ''),
    principles: Array.isArray(raw && raw.principles) ? raw.principles.map(String).filter(Boolean) : [],
  }
  try { fs.mkdirSync(c.workspace, { recursive: true }) } catch { /* noop */ }
  return c
}

const APPROVE_TOOLS = ['execute_shell', 'write_file', 'edit_file']
const PLAN_BLOCKED = ['execute_shell', 'write_file', 'edit_file']
const MAX_DELEGATE_DEPTH = 2

function needApproval(cfg: Config, name: string, args: any): boolean {
  if (!APPROVE_TOOLS.includes(name)) return false
  if (cfg.approve_mode === 'auto') return false
  if (cfg.approve_mode === 'whitelist' && name === 'execute_shell') {
    const cmd = String(args.command || '').trim()
    for (const w of cfg.whitelist) {
      if (w && (cmd === w || cmd.startsWith(w))) return false
    }
  }
  return true
}

function handleTodo(ss: SessionState, args: any, emit: (obj: any) => void) {
  const action = String(args.action || 'list')
  const find = (t: Todo) => (args.id && t.id === args.id) || (args.text && t.text === args.text)
  if (action === 'add' && args.text) {
    ss.todos.push({ id: Date.now().toString(36) + Math.random().toString(36).slice(2, 6), text: String(args.text), done: false })
  } else if (action === 'replace' && Array.isArray(args.items)) {
    ss.todos = args.items.map((t: any, i: number) => ({
      id: String(t.id || 't' + i + Date.now().toString(36)),
      text: String(t.text || ''),
      done: !!t.done,
    }))
  } else if (action === 'done' || action === 'undo' || action === 'remove') {
    const i = ss.todos.findIndex(find)
    if (i >= 0) {
      if (action === 'remove') ss.todos.splice(i, 1)
      else ss.todos[i].done = action === 'done'
    }
  } else if (action === 'clear') {
    ss.todos = []
  }
  emit({ type: 'todo', todos: ss.todos })
}

function readMemory(cfg: Config): string {
  try {
    return fs.existsSync(cfg.memory_path) ? fs.readFileSync(cfg.memory_path, 'utf-8').trim() : ''
  } catch { return '' }
}

function handleMemory(cfg: Config, args: any): string {
  const action = String(args.action || 'read')
  let cur = readMemory(cfg)
  if (action === 'read') {
    return cur ? cur : '(暂无长期记忆)'
  }
  if (action === 'add') {
    const text = String(args.text || '').trim()
    if (!text) return '缺少文本'
    cur = cur ? cur.trimEnd() + '\n- ' + text : '- ' + text
  } else if (action === 'replace') {
    cur = String(args.text || '').trim()
  } else if (action === 'clear') {
    cur = ''
  } else {
    return '未知 action (read/add/replace/clear)'
  }
  try {
    fs.writeFileSync(cfg.memory_path, cur, 'utf-8')
  } catch (e: any) { return '记忆写入失败: ' + ((e && e.message) || e) }
  return cur ? '记忆已更新:\n' + cur : '记忆已清空'
}

async function handleDelegate(
  cfg: Config,
  args: any,
  emit: (obj: any) => void,
  depth: number
): Promise<string> {
  if (depth <= 0) return '[子代理] 已达最大递归深度, 停止委派'
  const prompt = String(args.prompt || '').trim()
  if (!prompt) return '[子代理] 缺少 prompt'
  const subSystem = String(args.system || '').trim() ||
    '你是一个专注处理子任务的子代理。不要调用任何工具, 只根据给定任务直接给出结果。用中文回答。'
  const out = await streamChat(
    cfg,
    [{ role: 'system', content: subSystem }, { role: 'user', content: prompt }],
    [],
    {},
  )
  return out.content || '(子代理无输出)'
}

async function runToolWithEvents(cfg: Config, name: string, args: any, emit: (obj: any) => void): Promise<string> {
  emit({ type: 'tool', state: 'start', name, args })
  let content: string
  try {
    content = (await execTool(cfg, name, args)).content
  } catch (e: any) {
    content = '[工具错误] ' + ((e && e.message) || String(e))
  }
  emit({ type: 'tool', state: 'end', name, args, output: content.slice(0, 600) })
  return content
}

async function continueLoop(
  ss: SessionState,
  cfg: Config,
  skills: Skill[],
  emit: (obj: any) => void,
  depth = 0
): Promise<void> {
  if (depth > MAX_DELEGATE_DEPTH) { emit({ type: 'error', error: '超过最大子代理嵌套深度' }); return }
  const defs = buildToolDefs(skills)
  const system = buildSystemPrompt(cfg.principles, readMemory(cfg))
  const maxSteps = cfg.max_tool_steps || 40
  let steps = 0
  try {
    while (steps < maxSteps) {
      if (ss._cancel) { emit({ type: 'canceled' }); return }
      steps++
      const out = await streamChat(cfg, [{ role: 'system', content: system }, ...ss.messages], defs, {
        onContent: (d) => emit({ type: 'message', content: d }),
        onReasoning: () => emit({ type: 'thinking' }),
      })
      const assistant: AssistantMsg = {
        role: 'assistant',
        content: out.content,
        tool_calls: out.tool_calls.map((t) => ({ id: t.id, name: t.name, arguments: t.arguments })) as ToolCallArg[],
      }
      if (out.reasoning_content) assistant.reasoning_content = out.reasoning_content
      ss.messages.push(assistant)
      if (!out.tool_calls.length) {
        ss.updated = Date.now()
        ss.pending = null
        saveSession(ss)
        emit({ type: 'done', content: out.content })
        return
      }
      for (const tc of out.tool_calls) {
        if (ss._cancel) { emit({ type: 'canceled' }); return }
        let args: any = {}
        try { args = tc.arguments ? JSON.parse(tc.arguments) : {} } catch { args = { _raw: tc.arguments } }
        if (tc.name === 'update_todo') {
          handleTodo(ss, args, emit)
          ss.messages.push({ role: 'tool', tool_call_id: tc.id, content: '任务清单已更新' })
          saveSession(ss)
          continue
        }
        if (tc.name === 'memory') {
          const content = handleMemory(cfg, args)
          ss.messages.push({ role: 'tool', tool_call_id: tc.id, content })
          emit({ type: 'memory', content: readMemory(cfg) })
          saveSession(ss)
          continue
        }
        if (tc.name === 'delegate') {
          const content = await handleDelegate(cfg, args, emit, depth)
          ss.messages.push({ role: 'tool', tool_call_id: tc.id, content })
          emit({ type: 'tool', state: 'start', name: 'delegate', args })
          emit({ type: 'tool', state: 'end', name: 'delegate', args, output: content.slice(0, 600) })
          saveSession(ss)
          continue
        }
        // 用户自定义 skill: 函数型工具, 服务器端执行, 免审批
        if ((skills || []).some((s) => s.enabled && s.name === tc.name)) {
          const content = await execSkillByName(cfg, skills, tc.name, args)
          emit({ type: 'tool', state: 'start', name: tc.name, args })
          emit({ type: 'tool', state: 'end', name: tc.name, args, output: content.content.slice(0, 600) })
          ss.messages.push({ role: 'tool', tool_call_id: tc.id, content: content.content })
          ss.updated = Date.now()
          saveSession(ss)
          continue
        }
        if (cfg.agent_mode === 'plan' && PLAN_BLOCKED.includes(tc.name)) {
          ss.messages.push({
            role: 'tool', tool_call_id: tc.id,
            content: '[Plan 模式] 已阻止工具 %s: 规划模式只读, 不允许写文件/编辑/执行命令, 请切换到 build 模式执行'.replace('%s', tc.name),
          })
          saveSession(ss)
          continue
        }
        if (needApproval(cfg, tc.name, args)) {
          const pending: PendingTool = { tool_call_id: tc.id, name: tc.name, args, created: Date.now() }
          ss.pending = pending
          ss.updated = Date.now()
          saveSession(ss)
          emit({ type: 'approve', session_id: ss.id, name: tc.name, args })
          emit({ type: 'waiting' })
          return
        }
        const content = await runToolWithEvents(cfg, tc.name, args, emit)
        ss.messages.push({ role: 'tool', tool_call_id: tc.id, content })
        ss.updated = Date.now()
        saveSession(ss)
      }
      emit({ type: 'step_done', steps })
    }
    ss.pending = null
    saveSession(ss)
    emit({ type: 'error', error: '超过最大工具调用步数, 已停止' })
    emit({ type: 'done', content: '' })
  } catch (e: any) {
    ss.pending = null
    try { saveSession(ss) } catch { /* noop */ }
    emit({ type: 'error', error: (e && e.message) || String(e) })
    emit({ type: 'done', content: '' })
  }
}

async function handleChat(ss: SessionState, cfg: Config, skills: Skill[], emit: (obj: any) => void) {
  emit({ type: 'start' })
  emit({ type: 'todo', todos: ss.todos })
  await continueLoop(ss, cfg, skills, emit)
}

async function handleApprove(
  ss: SessionState,
  cfg: Config,
  skills: Skill[],
  approved: boolean,
  reason: string,
  emit: (obj: any) => void
) {
  const pending = ss.pending
  if (!pending) {
    emit({ type: 'error', error: '没有待审批的工具调用' })
    emit({ type: 'done', content: '' })
    return
  }
  ss.pending = null
  ss.updated = Date.now()
  saveSession(ss)
  if (!approved) {
    ss.messages.push({ role: 'tool', tool_call_id: pending.tool_call_id, content: redact('用户拒绝执行该工具调用' + (reason ? ': ' + reason : '')) })
  } else {
    const content = await runToolWithEvents(cfg, pending.name, pending.args, emit)
    ss.messages.push({ role: 'tool', tool_call_id: pending.tool_call_id, content })
  }
  ss.updated = Date.now()
  saveSession(ss)
  await continueLoop(ss, cfg, skills, emit)
}

// ---------------------------------------------------------------- HTTP / SSE

function sendJson(res: http.ServerResponse, code: number, obj: any) {
  const body = JSON.stringify(obj)
  res.writeHead(code, { 'Content-Type': 'application/json; charset=utf-8' })
  res.end(body)
}

function readBody(req: http.IncomingMessage): Promise<any> {
  return new Promise((resolve, reject) => {
    let data = ''
    req.on('data', (c) => {
      data += c
      if (data.length > 16 * 1024 * 1024) { req.destroy(); reject(new Error('body too large')) }
    })
    req.on('end', () => {
      try { resolve(data ? JSON.parse(data) : {}) } catch { reject(new Error('invalid json')) }
    })
    req.on('error', reject)
  })
}

function checkSecret(req: http.IncomingMessage): boolean {
  return !SECRET || req.headers['x-rc-secret'] === SECRET
}

function sseStart(res: http.ServerResponse) {
  res.writeHead(200, {
    'Content-Type': 'text/event-stream; charset=utf-8',
    'Cache-Control': 'no-cache',
    Connection: 'keep-alive',
    'X-Accel-Buffering': 'no',
  })
  res.flushHeaders()
  res.write('retry: 2000\n\n')
  return {
    emit: (obj: any) => { try { res.write('data: ' + JSON.stringify(obj) + '\n\n') } catch { /* noop */ } },
    end: () => { try { res.end() } catch { /* noop */ } },
  }
}

const server = http.createServer(async (req, res) => {
  const u = new URL(req.url || '/', 'http://localhost')
  try {
    if (u.pathname === '/health' && req.method === 'GET') {
      return sendJson(res, 200, { ok: true, version: VERSION, port: PORT, uptime: Math.round(process.uptime()) })
    }
    if (u.pathname === '/stop' && req.method === 'POST') {
      if (!checkSecret(req)) return sendJson(res, 401, { error: 'unauthorized' })
      setTimeout(() => process.exit(0), 300).unref()
      server.close(() => process.exit(0))
      return sendJson(res, 200, { ok: true })
    }
    if (u.pathname === '/cancel' && req.method === 'POST') {
      if (!checkSecret(req)) return sendJson(res, 401, { error: 'unauthorized' })
      const body = await readBody(req)
      const id = String(body.session_id || '')
      const ss = sessions.get(id)
      if (ss) { ss._cancel = true; ss._busy = false }
      return sendJson(res, 200, { ok: true })
    }
    if (u.pathname === '/chat' || u.pathname === '/approve') {
      if (req.method !== 'POST') return sendJson(res, 405, { error: 'method not allowed' })
      if (!checkSecret(req)) return sendJson(res, 401, { error: 'unauthorized' })
      const body = await readBody(req)
      const session_id = String(body.session_id || '')
      if (!session_id) return sendJson(res, 400, { error: '缺少 session_id' })
      const cfg = sanitizeConfig(body.config || {})
      const skills = sanitizeSkills(body.skills)
      const ss = getSession(session_id)
      if (ss._busy) return sendJson(res, 409, { error: '会话忙碌中, 请等待' })
      ss._busy = true
      ss._cancel = false
      const { emit, end } = sseStart(res)
      res.on('close', () => { ss._busy = false; ss._cancel = true })
      try {
        if (u.pathname === '/chat') {
          if (!cfg.api_key) throw new Error('未配置 API Key')
          ss.model = body.model || ss.model
          ss.workspace = cfg.workspace
          ss.active_skills = skills.map((s) => s.name)
          if (body.message) {
            ss.messages.push({ role: 'user', content: String(body.message) })
            if (!ss.title || ss.title === '新会话') ss.title = String(body.message).slice(0, 30)
          }
          saveSession(ss)
          await handleChat(ss, cfg, skills, emit)
        } else {
          await handleApprove(ss, cfg, skills, body.approved !== false, String(body.reason || ''), emit)
        }
      } catch (e: any) {
        emit({ type: 'error', error: (e && e.message) || String(e) })
        emit({ type: 'done', content: '' })
      } finally {
        ss._busy = false
        end()
      }
      return
    }
    return sendJson(res, 404, { error: 'not found' })
  } catch (e: any) {
    try { sendJson(res, 500, { error: (e && e.message) || String(e) }) } catch { /* noop */ }
  }
})

server.on('error', (e: any) => {
  console.error('[agent] 启动失败:', e && e.message)
  process.exit(1)
})

server.listen(PORT, '127.0.0.1', () => {
  console.log(`[raincode-agent] v${VERSION} listening on 127.0.0.1:${PORT} data=${DATA_DIR}`)
})

process.on('SIGTERM', () => {
  server.close(() => process.exit(0))
  setTimeout(() => process.exit(0), 500).unref()
})
process.on('SIGINT', () => {
  server.close(() => process.exit(0))
  setTimeout(() => process.exit(0), 500).unref()
})

setInterval(() => {
  const now = Date.now()
  for (const [id, ss] of sessions) {
    if (ss._busy) continue
    if (now - ss.updated > 24 * 3600 * 1000) sessions.delete(id)
  }
}, 30 * 60 * 1000).unref()
