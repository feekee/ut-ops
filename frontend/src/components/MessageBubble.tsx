import { memo } from 'react'
import ReactMarkdown from 'react-markdown'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism'
import {
  User,
  Terminal,
  Copy,
  Check,
  AlertCircle,
  Server,
  CheckCircle,
  XCircle,
} from 'lucide-react'
import { Message, ToolCall } from '../store/chatStore'
import { format } from 'date-fns'
import clsx from 'clsx'
import { useState } from 'react'

interface MessageBubbleProps {
  message: Message
  isLast?: boolean
}

function MessageBubble({ message, isLast }: MessageBubbleProps) {
  const [copiedCode, setCopiedCode] = useState<string | null>(null)
  const isUser = message.role === 'user'

  const copyToClipboard = (code: string) => {
    navigator.clipboard.writeText(code)
    setCopiedCode(code)
    setTimeout(() => setCopiedCode(null), 2000)
  }

  return (
    <div
      className={clsx(
        'flex gap-3 animate-slide-up',
        isUser ? 'flex-row-reverse' : 'flex-row'
      )}
    >
      {/* 头像 */}
      <div
        className={clsx(
          'w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0',
          isUser
            ? 'bg-primary-600'
            : 'bg-gradient-to-br from-accent-cyan to-primary-600'
        )}
      >
        {isUser ? (
          <User className="w-4 h-4 text-white" />
        ) : (
          <Terminal className="w-4 h-4 text-white" />
        )}
      </div>

      {/* 消息内容 */}
      <div className={clsx('flex flex-col gap-1 max-w-[80%]', isUser && 'items-end')}>
        {/* 角色标签 */}
        <div className="flex items-center gap-2 text-xs text-dark-500">
          <span>{isUser ? '你' : '智能运维助手'}</span>
          <span>•</span>
          <span>{format(new Date(message.timestamp), 'HH:mm')}</span>
          {message.status === 'error' && (
            <AlertCircle className="w-3 h-3 text-red-400" />
          )}
        </div>

        {/* 消息气泡 */}
        <div
          className={clsx(
            'message-bubble',
            isUser ? 'message-user' : 'message-assistant'
          )}
        >
          {isUser ? (
            <p className="whitespace-pre-wrap">{message.content}</p>
          ) : (
            <div className="prose prose-invert prose-sm max-w-none">
              <ReactMarkdown
                components={{
                  code({ node, className, children, ...props }) {
                    const match = /language-(\w+)/.exec(className || '')
                    const code = String(children).replace(/\n$/, '')
                    const isInline = !match && !code.includes('\n')

                    if (isInline) {
                      return (
                        <code
                          className="px-1.5 py-0.5 rounded bg-dark-700 text-accent-cyan font-mono text-sm"
                          {...props}
                        >
                          {children}
                        </code>
                      )
                    }

                    return (
                      <div className="code-block my-3 not-prose">
                        <div className="flex items-center justify-between px-4 py-2 bg-dark-900 border-b border-dark-700">
                          <span className="text-xs text-dark-400 font-mono">
                            {match ? match[1] : 'code'}
                          </span>
                          <button
                            onClick={() => copyToClipboard(code)}
                            className="flex items-center gap-1 text-xs text-dark-400 hover:text-dark-200 transition-colors"
                          >
                            {copiedCode === code ? (
                              <>
                                <Check className="w-3 h-3" />
                                <span>已复制</span>
                              </>
                            ) : (
                              <>
                                <Copy className="w-3 h-3" />
                                <span>复制</span>
                              </>
                            )}
                          </button>
                        </div>
                        <SyntaxHighlighter
                          style={oneDark}
                          language={match ? match[1] : 'text'}
                          PreTag="div"
                          customStyle={{
                            margin: 0,
                            background: 'transparent',
                            padding: '1rem',
                          }}
                        >
                          {code}
                        </SyntaxHighlighter>
                      </div>
                    )
                  },
                  p: ({ children }) => (
                    <p className="mb-2 last:mb-0 leading-relaxed">{children}</p>
                  ),
                  ul: ({ children }) => (
                    <ul className="list-disc list-inside mb-2 space-y-1">{children}</ul>
                  ),
                  ol: ({ children }) => (
                    <ol className="list-decimal list-inside mb-2 space-y-1">{children}</ol>
                  ),
                  li: ({ children }) => (
                    <li className="text-dark-200">{children}</li>
                  ),
                  a: ({ href, children }) => (
                    <a
                      href={href}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-accent-cyan hover:underline"
                    >
                      {children}
                    </a>
                  ),
                  strong: ({ children }) => (
                    <strong className="font-semibold text-dark-100">{children}</strong>
                  ),
                  h1: ({ children }) => (
                    <h1 className="text-lg font-bold text-dark-100 mt-4 mb-2">{children}</h1>
                  ),
                  h2: ({ children }) => (
                    <h2 className="text-base font-bold text-dark-100 mt-3 mb-2">{children}</h2>
                  ),
                  h3: ({ children }) => (
                    <h3 className="text-sm font-bold text-dark-100 mt-2 mb-1">{children}</h3>
                  ),
                  blockquote: ({ children }) => (
                    <blockquote className="border-l-2 border-accent-cyan pl-4 my-2 text-dark-300 italic">
                      {children}
                    </blockquote>
                  ),
                  table: ({ children }) => (
                    <div className="overflow-x-auto my-3">
                      <table className="w-full border-collapse border border-dark-700">
                        {children}
                      </table>
                    </div>
                  ),
                  th: ({ children }) => (
                    <th className="border border-dark-700 px-3 py-2 bg-dark-800 text-left font-medium">
                      {children}
                    </th>
                  ),
                  td: ({ children }) => (
                    <td className="border border-dark-700 px-3 py-2">{children}</td>
                  ),
                }}
              >
                {message.content}
              </ReactMarkdown>
            </div>
          )}
        </div>

        {/* 工具调用状态 */}
        {message.toolCalls && message.toolCalls.length > 0 && (
          <div className="mt-2 space-y-2">
            {message.toolCalls.map((tool, index) => (
              <ToolCallCard key={index} toolCall={tool} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

function ToolCallCard({ toolCall }: { toolCall: ToolCall }) {
  const statusConfig = {
    running: {
      icon: Server,
      color: 'text-accent-cyan',
      bgColor: 'bg-accent-cyan/10',
      label: '执行中...',
    },
    completed: {
      icon: CheckCircle,
      color: 'text-accent-green',
      bgColor: 'bg-accent-green/10',
      label: '完成',
    },
    error: {
      icon: XCircle,
      color: 'text-red-400',
      bgColor: 'bg-red-400/10',
      label: '失败',
    },
  }

  const config = statusConfig[toolCall.status]
  const Icon = config.icon

  return (
    <div className={clsx('rounded-lg p-3 border border-dark-700', config.bgColor)}>
      <div className="flex items-center gap-2 text-sm">
        <Icon className={clsx('w-4 h-4', config.color)} />
        <span className="font-medium text-dark-200">{toolCall.name}</span>
        <span className={clsx('text-xs', config.color)}>{config.label}</span>
      </div>
      {toolCall.output && (
        <pre className="mt-2 text-xs text-dark-400 font-mono whitespace-pre-wrap overflow-x-auto">
          {toolCall.output}
        </pre>
      )}
    </div>
  )
}

export default memo(MessageBubble)
