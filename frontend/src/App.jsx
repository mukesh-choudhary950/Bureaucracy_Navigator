import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import { QueryProvider } from './contexts/QueryContext'
import { TaskProvider } from './contexts/TaskContext'
import MainLayout from './components/MainLayout'
import Dashboard from './pages/Dashboard'
import DashboardSafe from './pages/DashboardSafe'
import TaskAssignment from './pages/TaskAssignment'
import ProcessSearch from './pages/ProcessSearch'
import WorkflowTracker from './pages/WorkflowTracker'
import Profile from './pages/Profile'
import Login from './pages/Login'
import Register from './pages/Register'
import './index.css'

function App() {
  return (
    <AuthProvider>
      <QueryProvider>
        <TaskProvider>
          <Router>
            <Routes>
              {/* Public Routes */}
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              
              {/* Protected Routes */}
              <Route path="/" element={<MainLayout />}>
                <Route index element={<Navigate to="/dashboard" replace />} />
                <Route path="dashboard" element={<DashboardSafe />} />
                <Route path="task-assignment" element={<TaskAssignment />} />
                <Route path="process-search" element={<ProcessSearch />} />
                <Route path="workflow-tracker" element={<WorkflowTracker />} />
                <Route path="profile" element={<Profile />} />
              </Route>
            </Routes>
          </Router>
        </TaskProvider>
      </QueryProvider>
    </AuthProvider>
  )
}

export default App
