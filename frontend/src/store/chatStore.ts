import { create } from 'zustand'

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  status?: 'sending' | 'sent' | 'error'
  toolCalls?: ToolCall[]
}

export interface ToolCall {
  name: string
  input: Record<string, unknown>
  output?: string
  status: 'running' | 'completed' | 'error'
}

export interface Conversation {
  id: string
  title: string
  messages: Message[]
  createdAt: Date
  updatedAt: Date
}

interface ChatState {
  conversations: Conversation[]
  activeConversationId: string | null
  isLoading: boolean
  
  // Actions
  createConversation: () => void
  setActiveConversation: (id: string) => void
  deleteConversation: (id: string) => void
  addMessage: (conversationId: string, message: Omit<Message, 'id' | 'timestamp'>) => void
  updateMessage: (conversationId: string, messageId: string, updates: Partial<Message>) => void
  setLoading: (loading: boolean) => void
  clearConversation: (id: string) => void
}

const generateId = () => Math.random().toString(36).substring(2, 15)

export const useChatStore = create<ChatState>((set, get) => ({
  conversations: [],
  activeConversationId: null,
  isLoading: false,

  createConversation: () => {
    const newConversation: Conversation = {
      id: generateId(),
      title: '新对话',
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    }
    
    set((state) => ({
      conversations: [newConversation, ...state.conversations],
      activeConversationId: newConversation.id,
    }))
  },

  setActiveConversation: (id: string) => {
    set({ activeConversationId: id })
  },

  deleteConversation: (id: string) => {
    set((state) => {
      const remaining = state.conversations.filter((c) => c.id !== id)
      return {
        conversations: remaining,
        activeConversationId: 
          state.activeConversationId === id 
            ? (remaining[0]?.id ?? null) 
            : state.activeConversationId,
      }
    })
  },

  addMessage: (conversationId: string, message: Omit<Message, 'id' | 'timestamp'>) => {
    const newMessage: Message = {
      ...message,
      id: generateId(),
      timestamp: new Date(),
    }

    set((state) => ({
      conversations: state.conversations.map((conv) => {
        if (conv.id === conversationId) {
          // 如果是第一条用户消息，更新对话标题
          const title = conv.messages.length === 0 && message.role === 'user'
            ? message.content.slice(0, 30) + (message.content.length > 30 ? '...' : '')
            : conv.title
          
          return {
            ...conv,
            title,
            messages: [...conv.messages, newMessage],
            updatedAt: new Date(),
          }
        }
        return conv
      }),
    }))

    return newMessage.id
  },

  updateMessage: (conversationId: string, messageId: string, updates: Partial<Message>) => {
    set((state) => ({
      conversations: state.conversations.map((conv) => {
        if (conv.id === conversationId) {
          return {
            ...conv,
            messages: conv.messages.map((msg) =>
              msg.id === messageId ? { ...msg, ...updates } : msg
            ),
            updatedAt: new Date(),
          }
        }
        return conv
      }),
    }))
  },

  setLoading: (loading: boolean) => {
    set({ isLoading: loading })
  },

  clearConversation: (id: string) => {
    set((state) => ({
      conversations: state.conversations.map((conv) =>
        conv.id === id
          ? { ...conv, messages: [], title: '新对话', updatedAt: new Date() }
          : conv
      ),
    }))
  },
}))
