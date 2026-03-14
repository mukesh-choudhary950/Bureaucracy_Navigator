'use client'

import { useState, useRef, useEffect } from 'react'
import { PaperAirplaneIcon, DocumentPlusIcon } from '@heroicons/react/24/outline'
import { useChatStore } from '@/store/chatStore'
import { useTaskStore } from '@/store/taskStore'

interface Message {
  id: string
  type: 'user' | 'agent'
  content: string
  timestamp: Date
  taskId?: number
  plan?: any
}

export default function ChatInterface() {
  const [message, setMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const { messages, addMessage } = useChatStore()
  const { createTask } = useTaskStore()

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!message.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: message,
      timestamp: new Date()
    }

    addMessage(userMessage)
    setMessage('')
    setIsLoading(true)

    try {
      const response = await fetch('/api/query/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          user_id: 1
        })
      })

      const data = await response.json()

      const agentMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'agent',
        content: data.response,
        timestamp: new Date(),
        taskId: data.task_id,
        plan: data.plan
      }

      addMessage(agentMessage)

      if (data.task_id) {
        createTask({
          id: data.task_id,
          title: `Task: ${message.substring(0, 50)}...`,
          description: message,
          status: 'in_progress',
          plan: data.plan,
          createdAt: new Date()
        })
      }

    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'agent',
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        timestamp: new Date()
      }
      addMessage(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage(e)
    }
  }

  const suggestedQueries = [
    "Apply for income certificate in Telangana",
    "How to get driving license",
    "Documents required for caste certificate",
    "Track my application status"
  ]

  return (
    <div className="flex flex-col h-[600px] bg-white rounded-lg shadow-sm border border-gray-200">
      {/* Chat Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">AI Assistant</h2>
        <p className="text-sm text-gray-600 mt-1">
          Ask me about government procedures and certificates
        </p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center py-8">
            <div className="text-4xl mb-4">🤖</div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Welcome to Bureaucracy Navigator!
            </h3>
            <p className="text-gray-600 mb-4">
              I can help you with government procedures and certificates. Try asking:
            </p>
            <div className="flex flex-wrap gap-2 justify-center">
              {suggestedQueries.map((query, index) => (
                <button
                  key={index}
                  onClick={() => setMessage(query)}
                  className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm hover:bg-gray-200 transition-colors"
                >
                  {query}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`message-bubble ${msg.type === 'user' ? 'message-user' : 'message-agent'}`}
            >
              <div className="whitespace-pre-wrap">{msg.content}</div>
              
              {msg.plan && (
                <div className="mt-3 p-3 bg-white bg-opacity-20 rounded">
                  <h4 className="font-medium mb-2">Generated Plan:</h4>
                  <div className="text-sm space-y-1">
                    {msg.plan.steps?.map((step: any, index: number) => (
                      <div key={index} className="flex items-center space-x-2">
                        <span className="w-5 h-5 bg-white bg-opacity-30 rounded-full flex items-center justify-center text-xs">
                          {index + 1}
                        </span>
                        <span>{step.description}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              <div className="text-xs mt-2 opacity-70">
                {msg.timestamp.toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="message-bubble message-agent">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse delay-75"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse delay-150"></div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="px-6 py-4 border-t border-gray-200">
        <form onSubmit={handleSendMessage} className="flex items-end space-x-3">
          <div className="flex-1">
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message here..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
              rows={2}
              disabled={isLoading}
            />
          </div>
          <button
            type="submit"
            disabled={!message.trim() || isLoading}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <PaperAirplaneIcon className="h-5 w-5" />
          </button>
        </form>
      </div>
    </div>
  )
}
