import React from 'react'
import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import Sidebar from './Sidebar'

const MainLayout = () => {
  const { user } = useAuth()

  // Redirect to login if not authenticated
  if (!user) {
    return <Navigate to="/login" replace />
  }

  return (
    <div className="flex h-screen">
      <Sidebar />
      <main 
        className="flex-1 overflow-auto"
        style={{
          background: 'linear-gradient(135deg, #dbeafe 0%, #e9d5ff 50%, #fce7f3 100%)',
          minHeight: '100vh'
        }}
      >
        <Outlet />
      </main>
    </div>
  )
}

export default MainLayout
