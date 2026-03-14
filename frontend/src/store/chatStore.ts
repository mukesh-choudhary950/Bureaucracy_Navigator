import { create } from 'zustand'

interface Message {
  id: string
  type: 'user' | 'agent'
  content: string
  timestamp: Date
  taskId?: number
  plan?: any
}

interface ChatStore {
  messages: Message[]
  addMessage: (message: Message) => void
  clearMessages: () => void
  isLoading: boolean
  setIsLoading: (loading: boolean) => void
}

export const useChatStore = create<ChatStore>((set) => ({
  messages: [],
  addMessage: (message) => set((state) => ({ 
    messages: [...state.messages, message] 
  })),
  clearMessages: () => set({ messages: [] }),
  isLoading: false,
  setIsLoading: (loading) => set({ isLoading: loading })
}))
