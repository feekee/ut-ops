import { useState } from 'react'
import {
  MessageSquarePlus,
  Settings,
  ChevronLeft,
  ChevronRight,
  Trash2,
  MessageSquare,
  Server,
  BookOpen,
  Terminal,
} from 'lucide-react'
import { useChatStore, Conversation } from '../store/chatStore'
import { format } from 'date-fns'
import { zhCN } from 'date-fns/locale'
import clsx from 'clsx'

interface SidebarProps {
  isOpen: boolean
  onToggle: () => void
}

export default function Sidebar({ isOpen, onToggle }: SidebarProps) {
  const { 
    conversations, 
    activeConversationId, 
    createConversation, 
    setActiveConversation,
    deleteConversation,
  } = useChatStore()

  const [hoveredId, setHoveredId] = useState<string | null>(null)

  const handleNewChat = () => {
    createConversation()
  }

  const handleDelete = (e: React.MouseEvent, id: string) => {
    e.stopPropagation()
    deleteConversation(id)
  }

  // 按日期分组对话
  const groupedConversations = conversations.reduce((groups, conv) => {
    const date = format(new Date(conv.updatedAt), 'yyyy-MM-dd')
    const today = format(new Date(), 'yyyy-MM-dd')
    const yesterday = format(new Date(Date.now() - 86400000), 'yyyy-MM-dd')
    
    let label = format(new Date(conv.updatedAt), 'MM月dd日', { locale: zhCN })
    if (date === today) label = '今天'
    else if (date === yesterday) label = '昨天'
    
    if (!groups[label]) groups[label] = []
    groups[label].push(conv)
    return groups
  }, {} as Record<string, Conversation[]>)

  return (
    <aside
      className={clsx(
        'h-full flex flex-col bg-dark-950/80 backdrop-blur-xl border-r border-dark-800/50',
        'transition-all duration-300 ease-in-out relative z-20',
        isOpen ? 'w-72' : 'w-0'
      )}
    >
      {isOpen && (
        <>
          {/* Logo 区域 */}
          <div className="p-4 border-b border-dark-800/50">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-accent-cyan to-primary-600 flex items-center justify-center glow">
                <Terminal className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-semibold gradient-text">智能运维助手</h1>
                <p className="text-xs text-dark-500">Smart O&M Assistant</p>
              </div>
            </div>
          </div>

          {/* 新建对话按钮 */}
          <div className="p-3">
            <button
              onClick={handleNewChat}
              className="w-full flex items-center gap-3 px-4 py-3 rounded-xl
                         bg-gradient-to-r from-primary-600/20 to-accent-cyan/20
                         border border-primary-500/30 hover:border-primary-500/50
                         text-dark-100 transition-all duration-200 group"
            >
              <MessageSquarePlus className="w-5 h-5 text-accent-cyan group-hover:scale-110 transition-transform" />
              <span className="font-medium">新建对话</span>
            </button>
          </div>

          {/* 快捷功能 */}
          <div className="px-3 pb-2">
            <div className="grid grid-cols-2 gap-2">
              <button className="sidebar-item text-sm justify-center">
                <Server className="w-4 h-4" />
                <span>服务器</span>
              </button>
              <button className="sidebar-item text-sm justify-center">
                <BookOpen className="w-4 h-4" />
                <span>知识库</span>
              </button>
            </div>
          </div>

          {/* 对话历史 */}
          <div className="flex-1 overflow-y-auto px-3 py-2">
            {Object.entries(groupedConversations).map(([label, convs]) => (
              <div key={label} className="mb-4">
                <div className="px-2 py-1.5 text-xs text-dark-500 font-medium">
                  {label}
                </div>
                <div className="space-y-1">
                  {convs.map((conv) => (
                    <div
                      key={conv.id}
                      onClick={() => setActiveConversation(conv.id)}
                      onMouseEnter={() => setHoveredId(conv.id)}
                      onMouseLeave={() => setHoveredId(null)}
                      className={clsx(
                        'sidebar-item group relative',
                        activeConversationId === conv.id && 'active'
                      )}
                    >
                      <MessageSquare className="w-4 h-4 flex-shrink-0" />
                      <span className="flex-1 truncate text-sm">{conv.title}</span>
                      
                      {hoveredId === conv.id && (
                        <button
                          onClick={(e) => handleDelete(e, conv.id)}
                          className="absolute right-2 p-1 rounded hover:bg-dark-700 
                                     text-dark-500 hover:text-red-400 transition-colors"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ))}

            {conversations.length === 0 && (
              <div className="text-center py-8 text-dark-500 text-sm">
                <MessageSquare className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p>暂无对话记录</p>
                <p className="text-xs mt-1">点击上方按钮开始新对话</p>
              </div>
            )}
          </div>

          {/* 底部设置 */}
          <div className="p-3 border-t border-dark-800/50">
            <button className="sidebar-item w-full">
              <Settings className="w-5 h-5" />
              <span>设置</span>
            </button>
          </div>
        </>
      )}

      {/* 折叠按钮 */}
      <button
        onClick={onToggle}
        className={clsx(
          'absolute top-1/2 -translate-y-1/2 w-6 h-12 rounded-r-lg',
          'bg-dark-800 border border-l-0 border-dark-700',
          'flex items-center justify-center text-dark-400 hover:text-dark-200',
          'transition-all duration-200 hover:w-7',
          isOpen ? '-right-6' : 'right-0 rounded-l-lg rounded-r-lg border-l'
        )}
      >
        {isOpen ? <ChevronLeft className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
      </button>
    </aside>
  )
}
