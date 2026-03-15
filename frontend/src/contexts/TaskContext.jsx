import React, { createContext, useContext, useState, useEffect } from 'react'
import axios from 'axios'

const TaskContext = createContext()

export const useTask = () => {
  const context = useContext(TaskContext)
  if (!context) {
    throw new Error('useTask must be used within a TaskProvider')
  }
  return context
}

export const TaskProvider = ({ children }) => {
  const [tasks, setTasks] = useState([])
  const [workflows, setWorkflows] = useState([])
  const [taskStats, setTaskStats] = useState({})
  const [workflowStats, setWorkflowStats] = useState({})
  const [loading, setLoading] = useState(false)

  const createTask = async (taskData) => {
    try {
      const response = await axios.post(`http://localhost:8000/api/v1/tasks/?username=${taskData.assigned_by}`, taskData)
      setTasks(prev => [response.data, ...prev])
      return response.data
    } catch (error) {
      console.error('Error creating task:', error)
      throw error
    }
  }

  const getTasks = async (username) => {
    try {
      setLoading(true)
      const response = await axios.get(`http://localhost:8000/api/v1/tasks/user/${username}`)
      setTasks(response.data)
      return response.data
    } catch (error) {
      console.error('Error getting tasks:', error)
      return []
    } finally {
      setLoading(false)
    }
  }

  const updateTaskStatus = async (taskId, status) => {
    try {
      await axios.put(`http://localhost:8000/api/v1/tasks/${taskId}/status`, { status })
      setTasks(prev => prev.map(task => 
        task.id === taskId ? { ...task, status } : task
      ))
    } catch (error) {
      console.error('Error updating task status:', error)
    }
  }

  const autoAssignTask = async (taskId) => {
    try {
      const response = await axios.post('http://localhost:8000/api/v1/tasks/auto-assign', {
        task_id: taskId
      })
      
      // Refresh tasks after auto-assignment
      await getTasks(user?.username)
      
      return response.data
    } catch (error) {
      console.error('Error auto-assigning task:', error)
      throw error
    }
  }

  const assignTask = async (taskId, assignedTo, reason = '') => {
    try {
      const response = await axios.post('http://localhost:8000/api/v1/tasks/assign', {
        task_id: taskId,
        assigned_to: assignedTo,
        reason: reason
      })
      
      // Update local state
      setTasks(prev => prev.map(task => 
        task.id === taskId ? { ...task, assigned_to: assignedTo } : task
      ))
      
      return response.data
    } catch (error) {
      console.error('Error assigning task:', error)
      throw error
    }
  }

  const getUnassignedTasks = async () => {
    try {
      setLoading(true)
      const response = await axios.get('http://localhost:8000/api/v1/tasks/unassigned/all')
      return response.data
    } catch (error) {
      console.error('Error getting unassigned tasks:', error)
      return []
    } finally {
      setLoading(false)
    }
  }

  const createWorkflow = async (workflowData, createdBy) => {
    try {
      const response = await axios.post(`http://localhost:8000/api/v1/workflows/?username=${createdBy}`, workflowData)
      setWorkflows(prev => [response.data, ...prev])
      return response.data
    } catch (error) {
      console.error('Error creating workflow:', error)
      throw error
    }
  }

  const getWorkflows = async (username) => {
    try {
      setLoading(true)
      const response = await axios.get(`http://localhost:8000/api/v1/workflows/user/${username}`)
      setWorkflows(response.data)
      return response.data
    } catch (error) {
      console.error('Error getting workflows:', error)
      return []
    } finally {
      setLoading(false)
    }
  }

  const getWorkflowSteps = async (workflowId) => {
    try {
      const response = await axios.get(`http://localhost:8000/api/v1/workflows/${workflowId}/steps`)
      return response.data
    } catch (error) {
      console.error('Error getting workflow steps:', error)
      return []
    }
  }

  const updateWorkflowStatus = async (workflowId, status) => {
    try {
      await axios.put(`http://localhost:8000/api/v1/workflows/${workflowId}/status`, { status })
      setWorkflows(prev => prev.map(workflow => 
        workflow.id === workflowId ? { ...workflow, status } : workflow
      ))
    } catch (error) {
      console.error('Error updating workflow status:', error)
    }
  }

  const getTaskStats = async (username) => {
    try {
      const response = await axios.get(`http://localhost:8000/api/v1/tasks/stats/${username}`)
      setTaskStats(response.data)
      return response.data
    } catch (error) {
      console.error('Error getting task stats:', error)
      return {}
    }
  }

  const getWorkflowStats = async (username) => {
    try {
      const response = await axios.get(`http://localhost:8000/api/v1/workflows/stats/${username}`)
      setWorkflowStats(response.data)
      return response.data
    } catch (error) {
      console.error('Error getting workflow stats:', error)
      return {}
    }
  }

  const value = {
    tasks,
    workflows,
    taskStats,
    workflowStats,
    loading,
    createTask,
    getTasks,
    updateTaskStatus,
    autoAssignTask,
    assignTask,
    getUnassignedTasks,
    createWorkflow,
    getWorkflows,
    getWorkflowSteps,
    updateWorkflowStatus,
    getTaskStats,
    getWorkflowStats
  }

  return (
    <TaskContext.Provider value={value}>
      {children}
    </TaskContext.Provider>
  )
}
