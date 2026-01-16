/**
 * API 服务
 */

const API_BASE_URL = '/api'

export interface ChatRequest {
  message: string
  conversationId?: string
  userId?: string
}

export interface ChatResponse {
  answer: string
  conversationId: string
  messageId: string
}

export interface SSHRequest {
  host: string
  command: string
  port?: number
}

export interface SSHResponse {
  success: boolean
  stdout: string
  stderr: string
  exitCode: number
}

export interface ServerStatus {
  host: string
  online: boolean
  cpuUsage?: string
  memoryUsage?: string
  diskUsage?: string
  loadAverage?: string
  uptime?: string
}

// Chat API
export async function sendMessage(request: ChatRequest): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/chat/send`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message: request.message,
      conversation_id: request.conversationId,
      user_id: request.userId || 'default_user',
    }),
  })

  if (!response.ok) {
    const error = await response.text()
    throw new Error(error || '发送消息失败')
  }

  const data = await response.json()
  return {
    answer: data.answer,
    conversationId: data.conversation_id,
    messageId: data.message_id,
  }
}

export async function* streamMessage(request: ChatRequest): AsyncGenerator<string> {
  const response = await fetch(`${API_BASE_URL}/chat/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message: request.message,
      conversation_id: request.conversationId,
      user_id: request.userId || 'default_user',
    }),
  })

  if (!response.ok) {
    throw new Error('流式请求失败')
  }

  const reader = response.body?.getReader()
  if (!reader) {
    throw new Error('无法读取响应')
  }

  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n\n')
    buffer = lines.pop() || ''

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = line.slice(6)
        try {
          const parsed = JSON.parse(data)
          if (parsed.answer) {
            yield parsed.answer
          }
        } catch {
          // 忽略解析错误
        }
      }
    }
  }
}

// SSH API
export async function executeSSHCommand(request: SSHRequest): Promise<SSHResponse> {
  const response = await fetch(`${API_BASE_URL}/ssh/execute`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      host: request.host,
      command: request.command,
      port: request.port || 22,
    }),
  })

  if (!response.ok) {
    const error = await response.text()
    throw new Error(error || 'SSH 命令执行失败')
  }

  const data = await response.json()
  return {
    success: data.success,
    stdout: data.stdout,
    stderr: data.stderr,
    exitCode: data.exit_code,
  }
}

export async function getServerStatus(host: string, port = 22): Promise<ServerStatus> {
  const response = await fetch(`${API_BASE_URL}/ssh/server-status`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ host, port }),
  })

  if (!response.ok) {
    throw new Error('获取服务器状态失败')
  }

  const data = await response.json()
  return {
    host: data.host,
    online: data.online,
    cpuUsage: data.cpu_usage,
    memoryUsage: data.memory_usage,
    diskUsage: data.disk_usage,
    loadAverage: data.load_average,
    uptime: data.uptime,
  }
}

export async function testSSHConnection(host: string, port = 22): Promise<boolean> {
  const response = await fetch(`${API_BASE_URL}/ssh/test-connection`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ host, port }),
  })

  if (!response.ok) {
    return false
  }

  const data = await response.json()
  return data.success
}
