'use client'

import { useState, useEffect } from 'react'
import ChatInterface from '@/components/ChatInterface'
import TaskProgress from '@/components/TaskProgress'
import DocumentUpload from '@/components/DocumentUpload'
import Header from '@/components/Header'
import { useTaskStore } from '@/store/taskStore'

export default function Home() {
  const [activeTab, setActiveTab] = useState('chat')
  const { tasks, fetchTasks } = useTaskStore()

  useEffect(() => {
    fetchTasks()
  }, [fetchTasks])

  const tabs = [
    { id: 'chat', name: 'Chat', icon: '💬' },
    { id: 'tasks', name: 'Tasks', icon: '📋' },
    { id: 'documents', name: 'Documents', icon: '📄' },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tab Navigation */}
        <div className="border-b border-gray-200 mb-8">
          <nav className="-mb-px flex space-x-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  py-2 px-1 border-b-2 font-medium text-sm
                  ${activeTab === tab.id
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.name}
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="space-y-6">
          {activeTab === 'chat' && <ChatInterface />}
          {activeTab === 'tasks' && <TaskProgress />}
          {activeTab === 'documents' && <DocumentUpload />}
        </div>
      </div>
    </div>
  )
}
