import React, { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { useTask } from '../contexts/TaskContext'
import { 
  Users, UserCheck, Calendar, Clock, CheckCircle, AlertTriangle, Play, 
  Search, X, UserPlus, Loader2, Plus 
} from 'lucide-react'
import axios from 'axios'

// Example tasks templates for government processes
const EXAMPLE_TASKS = [
  {
    id: 'template-1',
    icon: '🆔',
    title: 'Aadhaar Card Application Processing',
    description: 'Process new Aadhaar card applications including document verification, biometric capture, and enrollment ID generation.',
    priority: 'high',
    category: 'Identity',
    estimatedTime: '7-15 days',
    department: 'Identity Services',
    steps: 6,
    complexity: 'Medium',
    documents: ['Proof of Identity', 'Proof of Address', 'Date of Birth Proof', 'Photograph', 'Biometric Data']
  },
  {
    id: 'template-2',
    icon: '📄',
    title: 'Birth Certificate Registration',
    description: 'Register and issue birth certificates for newborns including hospital verification and database entry.',
    priority: 'medium',
    category: 'Civil Registration',
    estimatedTime: '5-10 days',
    department: 'Municipal Office',
    steps: 4,
    complexity: 'Low',
    documents: ['Hospital Birth Report', 'Parent ID Proof', 'Parent Address Proof', 'Marriage Certificate']
  },
  {
    id: 'template-3',
    icon: '🏠',
    title: 'Property Tax Assessment',
    description: 'Evaluate property values and calculate tax dues for residential and commercial properties.',
    priority: 'medium',
    category: 'Revenue',
    estimatedTime: '10-20 days',
    department: 'Revenue Department',
    steps: 5,
    complexity: 'High',
    documents: ['Property Documents', 'Previous Tax Receipts', 'Survey Number', 'Owner ID Proof']
  },
  {
    id: 'template-4',
    icon: '🏢',
    title: 'Business License Renewal',
    description: 'Process renewal of trade licenses for businesses including fee collection and certificate issuance.',
    priority: 'high',
    category: 'Commerce',
    estimatedTime: '3-7 days',
    department: 'Municipal Corporation',
    steps: 3,
    complexity: 'Low',
    documents: ['Previous License', 'Address Proof', 'GST Certificate', 'Fee Payment Receipt']
  },
  {
    id: 'template-5',
    icon: '🌾',
    title: 'Agriculture Subsidy Application',
    description: 'Review and process farmer subsidy applications including land verification and eligibility checks.',
    priority: 'high',
    category: 'Agriculture',
    estimatedTime: '15-30 days',
    department: 'Agriculture Department',
    steps: 7,
    complexity: 'High',
    documents: ['Land Ownership Proof', 'Farmer ID', 'Bank Account Details', 'Crop Details', 'Aadhaar Card']
  },
  {
    id: 'template-6',
    icon: '🚗',
    title: 'Vehicle Registration Transfer',
    description: 'Process ownership transfer of vehicles including document verification and RC update.',
    priority: 'medium',
    category: 'Transport',
    estimatedTime: '10-15 days',
    department: 'RTO',
    steps: 5,
    complexity: 'Medium',
    documents: ['Sale Deed', 'NOC from RTO', 'Insurance Certificate', 'Pollution Certificate', 'Address Proof']
  }
]

const TaskAssignment = () => {
  const { user } = useAuth()
  const { tasks, getTasks, autoAssignTask, assignTask, taskStats, getTaskStats, createTask } = useTask()
  
  const [localTasks, setLocalTasks] = useState([])
  const [loading, setLoading] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [selectedTask, setSelectedTask] = useState(null)
  const [assignmentMessage, setAssignmentMessage] = useState('')
  const [showAssignmentModal, setShowAssignmentModal] = useState(false)

  // Fetch tasks on mount
  useEffect(() => {
    if (user?.username) {
      fetchTasks()
    }
  }, [user])

  const fetchTasks = async () => {
    setLoading(true)
    try {
      const fetchedTasks = await getTasks(user.username)
      // Transform tasks to match the component format
      const formattedTasks = fetchedTasks.map(task => ({
        id: task.id,
        title: task.title,
        assignedTo: task.assigned_to || 'Unassigned',
        assignee: task.assigned_to || 'Unassigned',
        department: 'General', // Default department
        priority: task.priority || 'medium',
        status: task.status || 'pending',
        dueDate: task.due_date ? new Date(task.due_date).toISOString().split('T')[0] : 'Not set',
        estimatedTime: '3 days', // Default
        process: task.description || 'General Task'
      }))
      setLocalTasks(formattedTasks)
      await getTaskStats(user.username)
    } catch (error) {
      console.error('Error fetching tasks:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-100'
      case 'in-progress': return 'text-blue-600 bg-blue-100'
      case 'pending': return 'text-gray-600 bg-gray-100'
      case 'delayed': return 'text-red-600 bg-red-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'text-red-600 bg-red-100'
      case 'medium': return 'text-yellow-600 bg-yellow-100'
      case 'low': return 'text-gray-600 bg-gray-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  // Handle auto-assign for all unassigned tasks
  const handleAutoAssignAll = async () => {
    setLoading(true)
    try {
      const unassignedTasks = localTasks.filter(t => t.assignedTo === 'Unassigned' || !t.assignedTo)
      
      if (unassignedTasks.length === 0) {
        setAssignmentMessage('No unassigned tasks found!')
        setTimeout(() => setAssignmentMessage(''), 3000)
        return
      }

      let assignedCount = 0
      for (const task of unassignedTasks.slice(0, 3)) { // Auto-assign up to 3 tasks
        try {
          await autoAssignTask(task.id)
          assignedCount++
        } catch (error) {
          console.error(`Error auto-assigning task ${task.id}:`, error)
        }
      }

      await fetchTasks() // Refresh tasks
      setAssignmentMessage(`Successfully auto-assigned ${assignedCount} tasks!`)
      setTimeout(() => setAssignmentMessage(''), 3000)
    } catch (error) {
      console.error('Error in auto-assign:', error)
      setAssignmentMessage('Failed to auto-assign tasks. Please try again.')
      setTimeout(() => setAssignmentMessage(''), 3000)
    } finally {
      setLoading(false)
    }
  }

  // Handle auto-assign for single task
  const handleAutoAssignTask = async (taskId) => {
    setLoading(true)
    try {
      const result = await autoAssignTask(taskId)
      await fetchTasks() // Refresh tasks
      setAssignmentMessage(`Task assigned to ${result.assigned_to} based on workload!`)
      setTimeout(() => setAssignmentMessage(''), 3000)
    } catch (error) {
      console.error('Error auto-assigning task:', error)
      setAssignmentMessage('Failed to auto-assign task. Please try again.')
      setTimeout(() => setAssignmentMessage(''), 3000)
    } finally {
      setLoading(false)
    }
  }

  // Search users for assignment
  const searchUsers = async (query) => {
    if (!query || query.length < 2) {
      setSearchResults([])
      return
    }

    try {
      // In a real app, you'd have a user search endpoint
      // For now, we'll use a mock search based on common usernames
      const mockUsers = [
        { id: 1, username: 'john_doe', name: 'John Doe', department: 'Legal' },
        { id: 2, username: 'sarah_chen', name: 'Sarah Chen', department: 'Compliance' },
        { id: 3, username: 'mike_johnson', name: 'Mike Johnson', department: 'Finance' },
        { id: 4, username: 'alex_kumar', name: 'Alex Kumar', department: 'Operations' },
        { id: 5, username: 'priya_singh', name: 'Priya Singh', department: 'Operations' }
      ]
      
      const filtered = mockUsers.filter(u => 
        u.username.toLowerCase().includes(query.toLowerCase()) ||
        u.name.toLowerCase().includes(query.toLowerCase())
      )
      setSearchResults(filtered)
    } catch (error) {
      console.error('Error searching users:', error)
    }
  }

  // Handle manual assignment
  const handleManualAssign = async (username) => {
    if (!selectedTask) return
    
    setLoading(true)
    try {
      await assignTask(selectedTask.id, username, 'Manual assignment')
      await fetchTasks() // Refresh tasks
      setShowAssignmentModal(false)
      setSelectedTask(null)
      setSearchQuery('')
      setSearchResults([])
      setAssignmentMessage(`Task assigned to ${username}!`)
      setTimeout(() => setAssignmentMessage(''), 3000)
    } catch (error) {
      console.error('Error assigning task:', error)
      setAssignmentMessage('Failed to assign task. Please try again.')
      setTimeout(() => setAssignmentMessage(''), 3000)
    } finally {
      setLoading(false)
    }
  }

  // Open assignment modal
  const openAssignModal = (task) => {
    setSelectedTask(task)
    setShowAssignmentModal(true)
    setSearchQuery('')
    setSearchResults([])
  }

  // Create task from template
  const handleCreateFromTemplate = async (template) => {
    setLoading(true)
    try {
      // Create due date (7 days from now)
      const dueDate = new Date()
      dueDate.setDate(dueDate.getDate() + 7)

      const taskData = {
        title: template.title,
        description: template.description,
        assigned_to: '', // Leave unassigned so it can be auto-assigned
        priority: template.priority,
        due_date: dueDate.toISOString().split('T')[0]
      }

      const newTask = await createTask(taskData, user.username)
      
      if (newTask) {
        setAssignmentMessage(`Task "${template.title}" created from template! You can now assign it.`)
        await fetchTasks() // Refresh the task list
        setTimeout(() => setAssignmentMessage(''), 5000)
      } else {
        setAssignmentMessage('Failed to create task from template.')
        setTimeout(() => setAssignmentMessage(''), 3000)
      }
    } catch (error) {
      console.error('Error creating task from template:', error)
      setAssignmentMessage('Error creating task from template.')
      setTimeout(() => setAssignmentMessage(''), 3000)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Task Assignment Dashboard 📋
            </h1>
            <p className="text-gray-600">
              AI-powered task distribution and team management
            </p>
          </div>
          <button 
            onClick={handleAutoAssignAll}
            disabled={loading}
            className="px-4 py-2 bg-primary text-white rounded-md hover:bg-primary-dark disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
          >
            {loading ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Play className="h-4 w-4 mr-2" />
            )}
            Auto-Assign Tasks
          </button>
        </div>
        
        {/* Assignment Message */}
        {assignmentMessage && (
          <div className={`mt-4 p-3 rounded-md ${assignmentMessage.includes('Successfully') || assignmentMessage.includes('assigned to') ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
            {assignmentMessage}
          </div>
        )}
      </div>

      {/* Task Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center text-green-600">
            <CheckCircle className="h-8 w-8 mr-3" />
            <div>
              <p className="text-sm font-medium text-gray-600">Completed</p>
              <p className="text-2xl font-bold text-gray-900">{taskStats?.completed || 0}</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center text-blue-600">
            <Clock className="h-8 w-8 mr-3" />
            <div>
              <p className="text-sm font-medium text-gray-600">In Progress</p>
              <p className="text-2xl font-bold text-gray-900">{taskStats?.in_progress || 0}</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center text-yellow-600">
            <Calendar className="h-8 w-8 mr-3" />
            <div>
              <p className="text-sm font-medium text-gray-600">Pending</p>
              <p className="text-2xl font-bold text-gray-900">{taskStats?.pending || 0}</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center text-red-600">
            <AlertTriangle className="h-8 w-8 mr-3" />
            <div>
              <p className="text-sm font-medium text-gray-600">Unassigned</p>
              <p className="text-2xl font-bold text-gray-900">
                {localTasks.filter(t => t.assignedTo === 'Unassigned' || !t.assignedTo).length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Task List */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">
            Assigned Tasks
          </h2>
          <div className="text-sm text-gray-500">
            Total: {localTasks.length} tasks
          </div>
        </div>
        
        {loading ? (
          <div className="p-6 text-center">
            <Loader2 className="h-8 w-8 mx-auto animate-spin text-primary" />
            <p className="mt-2 text-gray-500">Loading tasks...</p>
          </div>
        ) : localTasks.length === 0 ? (
          <div className="p-6 text-center text-gray-500">
            No tasks found. Create a task to get started.
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {localTasks.map((task) => (
              <div key={task.id} className="p-6 hover:bg-gray-50">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center mb-2">
                      <h3 className="text-lg font-medium text-gray-900">
                        {task.title}
                      </h3>
                      <span className={`ml-3 px-2 py-1 text-xs font-medium rounded-full ${getPriorityColor(task.priority)}`}>
                        {task.priority.toUpperCase()}
                      </span>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
                      <div className="flex items-center">
                        <UserCheck className="h-4 w-4 mr-2" />
                        <span className={task.assignedTo === 'Unassigned' ? 'text-red-500 font-medium' : ''}>
                          {task.assignee}
                        </span>
                      </div>
                      <div className="flex items-center">
                        <Users className="h-4 w-4 mr-2" />
                        <span>{task.department}</span>
                      </div>
                      <div className="flex items-center">
                        <Calendar className="h-4 w-4 mr-2" />
                        <span>Due: {task.dueDate}</span>
                      </div>
                    </div>
                    
                    <div className="text-sm text-gray-500 mt-1">
                      Process: {task.process} • Est. {task.estimatedTime}
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2 mt-3">
                    <span className={`px-3 py-1 text-sm font-medium rounded-full ${getStatusColor(task.status)}`}>
                      {task.status.replace('-', ' ').toUpperCase()}
                    </span>
                    
                    {task.assignedTo === 'Unassigned' ? (
                      <button
                        onClick={() => handleAutoAssignTask(task.id)}
                        disabled={loading}
                        className="px-3 py-1 text-sm bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:opacity-50"
                      >
                        {loading ? <Loader2 className="h-3 w-3 animate-spin" /> : 'Auto Assign'}
                      </button>
                    ) : null}
                    
                    <button
                      onClick={() => openAssignModal(task)}
                      className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 flex items-center"
                    >
                      <UserPlus className="h-3 w-3 mr-1" />
                      Reassign
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Example Tasks Section */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">
              📋 Example Tasks
            </h2>
            <p className="text-sm text-gray-600">
              Pre-defined government process tasks ready for assignment
            </p>
          </div>
          <div className="text-sm text-gray-500">
            Click "Use Template" to create a new task
          </div>
        </div>

        <div className="divide-y divide-gray-200">
          {EXAMPLE_TASKS.map((exampleTask) => (
            <div key={exampleTask.id} className="p-6 hover:bg-gray-50">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center mb-2">
                    <span className="text-2xl mr-3">{exampleTask.icon}</span>
                    <h3 className="text-lg font-medium text-gray-900">
                      {exampleTask.title}
                    </h3>
                    <span className={`ml-3 px-2 py-1 text-xs font-medium rounded-full ${getPriorityColor(exampleTask.priority)}`}>
                      {exampleTask.priority.toUpperCase()}
                    </span>
                    <span className="ml-2 px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                      {exampleTask.category}
                    </span>
                  </div>
                  
                  <p className="text-sm text-gray-600 mb-3">
                    {exampleTask.description}
                  </p>
                  
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600">
                    <div className="flex items-center">
                      <Clock className="h-4 w-4 mr-2 text-gray-400" />
                      <span>Est. {exampleTask.estimatedTime}</span>
                    </div>
                    <div className="flex items-center">
                      <Users className="h-4 w-4 mr-2 text-gray-400" />
                      <span>{exampleTask.department}</span>
                    </div>
                    <div className="flex items-center">
                      <CheckCircle className="h-4 w-4 mr-2 text-gray-400" />
                      <span>{exampleTask.steps} steps</span>
                    </div>
                    <div className="flex items-center">
                      <AlertTriangle className="h-4 w-4 mr-2 text-gray-400" />
                      <span>{exampleTask.complexity}</span>
                    </div>
                  </div>

                  {/* Required Documents */}
                  <div className="mt-3">
                    <p className="text-xs text-gray-500 font-medium mb-1">Required Documents:</p>
                    <div className="flex flex-wrap gap-2">
                      {exampleTask.documents.slice(0, 3).map((doc, idx) => (
                        <span key={idx} className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded">
                          {doc}
                        </span>
                      ))}
                      {exampleTask.documents.length > 3 && (
                        <span className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded">
                          +{exampleTask.documents.length - 3} more
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2 mt-3 ml-4">
                  <button
                    onClick={() => handleCreateFromTemplate(exampleTask)}
                    disabled={loading}
                    className="px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 disabled:opacity-50 flex items-center text-sm"
                  >
                    <Plus className="h-4 w-4 mr-1" />
                    Use Template
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Assignment Modal */}
      {showAssignmentModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md mx-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">
                Assign Task: {selectedTask?.title}
              </h3>
              <button 
                onClick={() => {
                  setShowAssignmentModal(false)
                  setSelectedTask(null)
                  setSearchQuery('')
                  setSearchResults([])
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Search User to Assign
              </label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => {
                    setSearchQuery(e.target.value)
                    searchUsers(e.target.value)
                  }}
                  placeholder="Type username or name..."
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-transparent"
                />
              </div>
            </div>
            
            {/* Search Results */}
            {searchResults.length > 0 && (
              <div className="mb-4 max-h-48 overflow-y-auto border border-gray-200 rounded-md">
                {searchResults.map((userResult) => (
                  <button
                    key={userResult.id}
                    onClick={() => handleManualAssign(userResult.username)}
                    disabled={loading}
                    className="w-full px-4 py-3 text-left hover:bg-gray-50 border-b border-gray-100 last:border-0 flex items-center disabled:opacity-50"
                  >
                    <UserCheck className="h-4 w-4 mr-3 text-gray-400" />
                    <div className="flex-1">
                      <div className="font-medium text-gray-900">{userResult.name}</div>
                      <div className="text-sm text-gray-500">@{userResult.username} • {userResult.department}</div>
                    </div>
                  </button>
                ))}
              </div>
            )}
            
            {searchQuery && searchResults.length === 0 && (
              <div className="mb-4 p-3 text-center text-gray-500 text-sm">
                No users found matching "{searchQuery}"
              </div>
            )}
            
            <div className="flex space-x-3">
              <button
                onClick={() => {
                  setShowAssignmentModal(false)
                  setSelectedTask(null)
                  setSearchQuery('')
                  setSearchResults([])
                }}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={() => selectedTask && handleAutoAssignTask(selectedTask.id)}
                disabled={loading}
                className="flex-1 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:opacity-50 flex items-center justify-center"
              >
                {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <><Play className="h-4 w-4 mr-2" /> Auto Assign</>}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default TaskAssignment