import React, { useState, useEffect } from 'react'
import { useTask } from '../contexts/TaskContext'
import { useAuth } from '../contexts/AuthContext'
import { 
  GitBranch, 
  Plus, 
  Play, 
  Pause, 
  Check, 
  Clock,
  Calendar,
  User,
  TrendingUp,
  AlertCircle
} from 'lucide-react'

const WorkflowTracker = () => {
  const { user } = useAuth()
  const { 
    workflows, 
    getWorkflows, 
    getWorkflowSteps, 
    updateWorkflowStatus, 
    getWorkflowStats,
    createWorkflow,
    loading 
  } = useTask()
  
  const [selectedWorkflow, setSelectedWorkflow] = useState(null)
  const [workflowSteps, setWorkflowSteps] = useState([])
  const [stats, setStats] = useState({})
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    priority: 'medium',
    start_date: '',
    end_date: ''
  })

  useEffect(() => {
    if (user?.name) {
      loadWorkflows()
      loadStats()
    }
  }, [user])

  const loadWorkflows = async () => {
    await getWorkflows(user.name)
  }

  const loadStats = async () => {
    const workflowStats = await getWorkflowStats(user.name)
    setStats(workflowStats)
  }

  const handleWorkflowClick = async (workflow) => {
    setSelectedWorkflow(workflow)
    const steps = await getWorkflowSteps(workflow.id)
    setWorkflowSteps(steps)
  }

  const handleCreateWorkflow = async (e) => {
    e.preventDefault()
    try {
      await createWorkflow(formData, user.name)
      setShowCreateForm(false)
      setFormData({
        title: '',
        description: '',
        priority: 'medium',
        start_date: '',
        end_date: ''
      })
      loadWorkflows()
      loadStats()
    } catch (error) {
      console.error('Error creating workflow:', error)
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'not_started':
        return 'bg-gray-100 text-gray-700 border-gray-200'
      case 'in_progress':
        return 'bg-blue-100 text-blue-700 border-blue-200'
      case 'completed':
        return 'bg-green-100 text-green-700 border-green-200'
      case 'on_hold':
        return 'bg-yellow-100 text-yellow-700 border-yellow-200'
      default:
        return 'bg-gray-100 text-gray-700 border-gray-200'
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'not_started':
        return <Clock className="w-4 h-4" />
      case 'in_progress':
        return <Play className="w-4 h-4" />
      case 'completed':
        return <Check className="w-4 h-4" />
      case 'on_hold':
        return <Pause className="w-4 h-4" />
      default:
        return <AlertCircle className="w-4 h-4" />
    }
  }

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high':
        return 'text-red-600 bg-red-100'
      case 'medium':
        return 'text-yellow-600 bg-yellow-100'
      case 'low':
        return 'text-green-600 bg-green-100'
      default:
        return 'text-gray-600 bg-gray-100'
    }
  }

  const getStepIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'in-progress':
        return <Clock className="h-4 w-4 text-blue-500" />
      case 'pending':
        return <Clock className="h-4 w-4 text-gray-400" />
      case 'delayed':
        return <AlertTriangle className="h-4 w-4 text-red-500" />
      default:
        return <Clock className="h-4 w-4 text-gray-400" />
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Workflow Progress Tracker 📊
            </h1>
            <p className="text-gray-600">
              Real-time monitoring of government process workflows
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <button className="px-4 py-2 bg-primary text-white rounded-md hover:bg-primary-dark">
              <TrendingUp className="h-4 w-4 mr-2" />
              AI Insights
            </button>
            <button className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50">
              Export Report
            </button>
          </div>
        </div>
      </div>

      {/* Workflow Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {workflows.map((workflow) => (
          <div key={workflow.id} className="bg-white rounded-lg shadow">
            <div className="p-6">
              {/* Header */}
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-lg font-semibold text-gray-900">
                    {workflow.name}
                  </h2>
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getPriorityColor(workflow.priority)}`}>
                      {workflow.priority.toUpperCase()}
                    </span>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(workflow.status)}`}>
                      {workflow.status.replace('-', ' ').toUpperCase()}
                    </span>
                  </div>
                </div>
                
                <div className="text-right">
                  <div className="text-sm text-gray-500">
                    {workflow.startDate} - {workflow.estimatedCompletion}
                  </div>
                  <div className="text-2xl font-bold text-gray-900">
                    {workflow.progress}%
                  </div>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="mb-4">
                <div className="flex justify-between text-sm text-gray-600 mb-1">
                  <span>Progress</span>
                  <span>{workflow.progress}% Complete</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full ${workflow.progress === 100 ? 'bg-green-500' : 'bg-blue-500'}`}
                    style={{ width: `${workflow.progress}%` }}
                  ></div>
                </div>
              </div>

              {/* Steps */}
              <div className="space-y-3">
                <h3 className="text-sm font-medium text-gray-900 mb-3">
                  Process Steps
                </h3>
                {workflow.steps.map((step, index) => (
                  <div key={step.id} className="flex items-center p-3 bg-gray-50 rounded-lg">
                    <div className="mr-3">
                      {getStepIcon(step.status)}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-medium text-gray-900">
                            {index + 1}. {step.name}
                          </div>
                          <div className="text-sm text-gray-600">
                            Assigned to: {step.assignee}
                          </div>
                        </div>
                        <div className="text-right">
                          <div className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(step.status)}`}>
                            {step.status.replace('-', ' ').toUpperCase()}
                          </div>
                        </div>
                      </div>
                      
                      {step.dueDate && (
                        <div className="text-sm text-gray-500 mt-1">
                          Due: {step.dueDate}
                        </div>
                      )}
                      
                      {step.completedAt && (
                        <div className="text-sm text-green-600 mt-1">
                          ✅ Completed: {step.completedAt}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* AI Insights Panel */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          🤖 AI Workflow Insights
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="border-l-4 border-blue-500 pl-4">
            <h3 className="font-medium text-blue-900 mb-2">Bottleneck Detection</h3>
            <p className="text-sm text-gray-700">
              "Restaurant Permit Process" is delayed at Fire Safety Clearance step. Recommend reassigning to external certified inspector.
            </p>
            <div className="text-xs text-gray-500 mt-2">
              AI Confidence: 92% • Based on historical completion patterns
            </div>
          </div>
          
          <div className="border-l-4 border-green-500 pl-4">
            <h3 className="font-medium text-green-900 mb-2">Optimization Suggestion</h3>
            <p className="text-sm text-gray-700">
              "Food Business License" workflow is 23% faster than average. Consider using this template for similar processes.
            </p>
            <div className="text-xs text-gray-500 mt-2">
              AI Confidence: 87% • Based on 47 historical workflows
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default WorkflowTracker
