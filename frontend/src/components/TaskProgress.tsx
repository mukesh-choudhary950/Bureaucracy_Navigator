'use client'

import { useState, useEffect } from 'react'
import { useTaskStore } from '@/store/taskStore'
import { 
  CheckCircleIcon, 
  ClockIcon, 
  ExclamationCircleIcon,
  ArrowPathIcon 
} from '@heroicons/react/24/outline'

interface Task {
  id: number
  title: string
  description: string
  status: 'pending' | 'in_progress' | 'completed' | 'failed'
  plan?: any
  results?: any
  createdAt: Date
  updatedAt?: Date
}

export default function TaskProgress() {
  const { tasks, fetchTasks, updateTask } = useTaskStore()
  const [selectedTask, setSelectedTask] = useState<Task | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchTasks()
  }, [fetchTasks])

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />
      case 'in_progress':
        return <ClockIcon className="h-5 w-5 text-blue-500 animate-spin" />
      case 'failed':
        return <ExclamationCircleIcon className="h-5 w-5 text-red-500" />
      default:
        return <ClockIcon className="h-5 w-5 text-gray-400" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800'
      case 'in_progress':
        return 'bg-blue-100 text-blue-800'
      case 'failed':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const handleRetryTask = async (taskId: number) => {
    setLoading(true)
    try {
      const response = await fetch(`/api/query/task/${taskId}/retry`, {
        method: 'POST'
      })
      
      if (response.ok) {
        updateTask(taskId, { status: 'in_progress' })
        fetchTasks() // Refresh tasks
      }
    } catch (error) {
      console.error('Failed to retry task:', error)
    } finally {
      setLoading(false)
    }
  }

  const getProgressPercentage = (task: Task) => {
    if (!task.plan?.steps) return 0
    
    const totalSteps = task.plan.steps.length
    const completedSteps = task.plan.steps.filter((step: any) => 
      step.status === 'completed'
    ).length
    
    return Math.round((completedSteps / totalSteps) * 100)
  }

  if (tasks.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-4xl mb-4">📋</div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">No tasks yet</h3>
        <p className="text-gray-600">
          Start a conversation with the AI assistant to create tasks.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Task List */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {tasks.map((task) => (
          <div
            key={task.id}
            onClick={() => setSelectedTask(task)}
            className="card cursor-pointer hover:shadow-md transition-shadow"
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center space-x-2">
                {getStatusIcon(task.status)}
                <h3 className="font-medium text-gray-900 truncate">
                  {task.title}
                </h3>
              </div>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(task.status)}`}>
                {task.status.replace('_', ' ')}
              </span>
            </div>

            <p className="text-sm text-gray-600 mb-3 line-clamp-2">
              {task.description}
            </p>

            {/* Progress Bar */}
            {task.plan?.steps && (
              <div className="mb-3">
                <div className="flex justify-between text-xs text-gray-500 mb-1">
                  <span>Progress</span>
                  <span>{getProgressPercentage(task)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-primary-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${getProgressPercentage(task)}%` }}
                  ></div>
                </div>
              </div>
            )}

            <div className="flex items-center justify-between text-xs text-gray-500">
              <span>Created: {task.createdAt.toLocaleDateString()}</span>
              {task.status === 'failed' && (
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    handleRetryTask(task.id)
                  }}
                  disabled={loading}
                  className="flex items-center space-x-1 text-blue-600 hover:text-blue-700"
                >
                  <ArrowPathIcon className="h-3 w-3" />
                  <span>Retry</span>
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Task Details Modal */}
      {selectedTask && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h2 className="text-xl font-semibold text-gray-900 mb-2">
                    {selectedTask.title}
                  </h2>
                  <div className="flex items-center space-x-2">
                    {getStatusIcon(selectedTask.status)}
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(selectedTask.status)}`}>
                      {selectedTask.status.replace('_', ' ')}
                    </span>
                  </div>
                </div>
                <button
                  onClick={() => setSelectedTask(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <h3 className="font-medium text-gray-900 mb-2">Description</h3>
                  <p className="text-gray-600">{selectedTask.description}</p>
                </div>

                {selectedTask.plan?.steps && (
                  <div>
                    <h3 className="font-medium text-gray-900 mb-2">Plan Steps</h3>
                    <div className="space-y-2">
                      {selectedTask.plan.steps.map((step: any, index: number) => (
                        <div key={index} className="flex items-center space-x-3 p-3 bg-gray-50 rounded">
                          <div className="flex-shrink-0">
                            {step.status === 'completed' ? (
                              <CheckCircleIcon className="h-5 w-5 text-green-500" />
                            ) : step.status === 'failed' ? (
                              <ExclamationCircleIcon className="h-5 w-5 text-red-500" />
                            ) : (
                              <div className="h-5 w-5 border-2 border-gray-300 rounded-full" />
                            )}
                          </div>
                          <div className="flex-1">
                            <p className="text-sm font-medium text-gray-900">
                              {step.description}
                            </p>
                            {step.tool && (
                              <p className="text-xs text-gray-500">
                                Tool: {step.tool}
                              </p>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {selectedTask.results && (
                  <div>
                    <h3 className="font-medium text-gray-900 mb-2">Results</h3>
                    <div className="bg-gray-50 p-4 rounded">
                      <pre className="text-sm text-gray-600 whitespace-pre-wrap">
                        {JSON.stringify(selectedTask.results, null, 2)}
                      </pre>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
