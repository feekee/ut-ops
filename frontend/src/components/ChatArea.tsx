import { useState, useRef, useEffect } from 'react'
import {
  Send,
  Loader2,
  Menu,
  Sparkles,
  Server,
  FileText,
  Terminal,
  Cpu,
  HardDrive,
  Activity,
} from 'lucide-react'
import { useChatStore, Message } from '../store/chatStore'
import { sendMessage } from '../services/api'
import MessageBubble from './MessageBubble'
import clsx from 'clsx'

interface ChatAreaProps {
  sidebarOpen: boolean
  onToggleSidebar: () => void
}

// 快捷功能卡片
const quickActions = [
  {
    icon: Server,
    title: '服务器状态检查',
    description: '检查服务器 CPU、内存、磁盘使用情况',
    prompt: '请帮我检查服务器 192.168.1.100 的状态，包括 CPU、内存和磁盘使用情况',
    color: 'from-cyan-500 to-blue-500',
  },
  {
    icon: Activity,
    title: '容器状态监控',
    description: '查看 Docker 容器运行状态',
    prompt: '请帮我查看 192.168.1.100 上所有 Docker 容器的运行状态',
    color: 'from-purple-500 to-pink-500',
  },
  {
    icon: FileText,
    title: '日志分析',
    description: '分析服务日志查找异常',
    prompt: '请帮我分析 192.168.1.100 上的系统日志，查找最近的错误和警告',
    color: 'from-orange-500 to-red-500',
  },
  {
    icon: HardDrive,
    title: 'Kubernetes 状态',
    description: '检查 K8s 集群 Pod 状态',
    prompt: '请帮我检查 192.168.1.100 上的 Kubernetes 集群状态，列出所有 Pod',
    color: 'from-green-500 to-teal-500',
  },
]

export default function ChatArea({ sidebarOpen, onToggleSidebar }: ChatAreaProps) {
  const [input, setInput] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const {
    conversations,
    activeConversationId,
    isLoading,
    createConversation,
    addMessage,
    updateMessage,
    setLoading,
  } = useChatStore()

  const activeConversation = conversations.find((c) => c.id === activeConversationId)
  const messages = activeConversation?.messages || []

  // 滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // 自动调整输入框高度
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = 'auto'
      inputRef.current.style.height = `${Math.min(inputRef.current.scrollHeight, 200)}px`
    }
  }, [input])

  const handleSend = async (messageText?: string) => {
    const text = messageText || input.trim()
    if (!text || isLoading) return

    // 如果没有活动对话，创建一个新的
    let conversationId = activeConversationId
    if (!conversationId) {
      createConversation()
      // 需要等待 store 更新
      await new Promise((resolve) => setTimeout(resolve, 0))
      conversationId = useChatStore.getState().activeConversationId
    }

    if (!conversationId) return

    // 清空输入
    setInput('')

    // 添加用户消息
    addMessage(conversationId, {
      role: 'user',
      content: text,
      status: 'sent',
    })

    // 发送请求
    setLoading(true)
    setIsTyping(true)

    try {
      const response = await sendMessage({
        message: text,
        conversationId,
      })

      addMessage(conversationId, {
        role: 'assistant',
        content: response.answer,
        status: 'sent',
      })
    } catch (error) {
      console.error('发送消息失败:', error)
      addMessage(conversationId, {
        role: 'assistant',
        content: '抱歉，发生了错误。请稍后重试。',
        status: 'error',
      })
    } finally {
      setLoading(false)
      setIsTyping(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleQuickAction = (prompt: string) => {
    handleSend(prompt)
  }

  return (
    <div className="flex-1 flex flex-col h-full">
      {/* 头部 */}
      <header className="h-14 flex items-center justify-between px-4 border-b border-dark-800/50 bg-dark-900/50 backdrop-blur-sm">
        <div className="flex items-center gap-3">
          {!sidebarOpen && (
            <button onClick={onToggleSidebar} className="btn-ghost">
              <Menu className="w-5 h-5" />
            </button>
          )}
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-accent-green animate-pulse" />
            <span className="text-sm text-dark-400">
              {activeConversation?.title || '智能运维助手'}
            </span>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <span className="text-xs text-dark-500 px-2 py-1 rounded-full bg-dark-800">
            Qwen3-32B
          </span>
        </div>
      </header>

      {/* 消息区域 */}
      <div className="flex-1 overflow-y-auto">
        {messages.length === 0 ? (
          // 欢迎页面
          <div className="h-full flex flex-col items-center justify-center p-8">
            <div className="max-w-2xl w-full space-y-8 animate-fade-in">
              {/* Logo */}
              <div className="text-center">
                <div className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-accent-cyan to-primary-600 flex items-center justify-center glow-accent">
                  <Sparkles className="w-10 h-10 text-white" />
                </div>
                <h2 className="text-3xl font-bold gradient-text mb-2">
                  智能运维助手
                </h2>
                <p className="text-dark-400">
                  我可以帮助你进行服务器运维、故障排查和技术问答
                </p>
              </div>

              {/* 快捷功能 */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {quickActions.map((action, index) => (
                  <button
                    key={index}
                    onClick={() => handleQuickAction(action.prompt)}
                    className={clsx(
                      'group p-4 rounded-xl text-left',
                      'bg-dark-800/50 border border-dark-700/50',
                      'hover:border-dark-600 hover:bg-dark-800',
                      'transition-all duration-200',
                      'animate-slide-up',
                      `animation-delay-${index * 100}`
                    )}
                    style={{ animationDelay: `${index * 100}ms` }}
                  >
                    <div className="flex items-start gap-3">
                      <div className={clsx(
                        'w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0',
                        'bg-gradient-to-br',
                        action.color
                      )}>
                        <action.icon className="w-5 h-5 text-white" />
                      </div>
                      <div>
                        <h3 className="font-medium text-dark-100 group-hover:text-white transition-colors">
                          {action.title}
                        </h3>
                        <p className="text-sm text-dark-500 mt-0.5">
                          {action.description}
                        </p>
                      </div>
                    </div>
                  </button>
                ))}
              </div>

              {/* 提示 */}
              <p className="text-center text-sm text-dark-500">
                提示：你可以直接输入问题，或者点击上方卡片快速开始
              </p>
            </div>
          </div>
        ) : (
          // 消息列表
          <div className="max-w-4xl mx-auto p-4 space-y-6">
            {messages.map((message, index) => (
              <MessageBubble 
                key={message.id} 
                message={message} 
                isLast={index === messages.length - 1}
              />
            ))}

            {/* 正在输入指示器 */}
            {isTyping && (
              <div className="flex items-start gap-3 animate-fade-in">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-accent-cyan to-primary-600 flex items-center justify-center flex-shrink-0">
                  <Terminal className="w-4 h-4 text-white" />
                </div>
                <div className="message-bubble message-assistant">
                  <div className="flex items-center gap-2">
                    <Loader2 className="w-4 h-4 animate-spin text-accent-cyan" />
                    <span className="text-dark-400">正在思考...</span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* 输入区域 */}
      <div className="p-4 border-t border-dark-800/50 bg-dark-900/50 backdrop-blur-sm">
        <div className="max-w-4xl mx-auto">
          <div className="relative flex items-end gap-2">
            <div className="flex-1 relative">
              <textarea
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="输入你的问题，比如：请帮我检查 192.168.1.100 的服务状态..."
                className="input-modern min-h-[48px] max-h-[200px] pr-12 resize-none"
                rows={1}
                disabled={isLoading}
              />
              <button
                onClick={() => handleSend()}
                disabled={!input.trim() || isLoading}
                className={clsx(
                  'absolute right-2 bottom-2 p-2 rounded-lg transition-all duration-200',
                  input.trim() && !isLoading
                    ? 'bg-primary-600 hover:bg-primary-500 text-white'
                    : 'bg-dark-700 text-dark-500 cursor-not-allowed'
                )}
              >
                {isLoading ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Send className="w-5 h-5" />
                )}
              </button>
            </div>
          </div>
          <p className="text-xs text-dark-500 mt-2 text-center">
            按 Enter 发送，Shift + Enter 换行 • 智能运维助手可能会出错，请验证重要信息
          </p>
        </div>
      </div>
    </div>
  )
}
