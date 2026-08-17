export interface Config {
  api_base: string
  api_key: string
  model: string
  workspace: string
  approve_mode: 'auto' | 'confirm' | 'whitelist'
  whitelist: string[]
  shell_timeout: number
  output_cap: number
  max_tool_steps: number
}

export interface Skill {
  name: string
  title: string
  description: string
  instructions: string
  enabled: boolean
  builtin?: boolean
}

export type Role = 'system' | 'user' | 'assistant' | 'tool'

export interface ToolCallArg {
  id: string
  name: string
  arguments: string
}

export interface ToolCall {
  id: string
  name: string
  args: any
}

export interface AssistantMsg {
  role: 'assistant'
  content: string
  reasoning_content?: string
  tool_calls?: ToolCallArg[]
}

export type Message =
  | { role: 'system' | 'user'; content: string }
  | AssistantMsg
  | { role: 'tool'; tool_call_id: string; content: string }

export interface Todo {
  id: string
  text: string
  done: boolean
}

export interface PendingTool {
  tool_call_id: string
  name: string
  args: any
  created: number
}

export interface SessionState {
  id: string
  title: string
  created: number
  updated: number
  messages: Message[]
  todos: Todo[]
  pending: PendingTool | null
  active_skills: string[]
  model: string | null
  _busy?: boolean
  _cancel?: boolean
}
