import React, { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { 
  Home, 
  Search, 
  Users, 
  BarChart3, 
  Settings, 
  LogOut,
  Wifi,
  WifiOff
} from 'lucide-react'

const Layout = ({ children }) => {
  const { user, logout } = useAuth()
  const [backendStatus, setBackendStatus] = useState('checking')

  useEffect(() => {
    const checkBackendStatus = async () => {
      try {
        const response = await fetch('http://localhost:8000/health')
        if (response.ok) {
          setBackendStatus('connected')
        } else {
          setBackendStatus('error')
        }
      } catch (error) {
        setBackendStatus('disconnected')
      }
    }

    checkBackendStatus()
    const interval = setInterval(checkBackendStatus, 10000) // Check every 10 seconds

    return () => clearInterval(interval)
  }, [])

  const navigation = [
    { name: 'Dashboard', href: '/', icon: Home },
    { name: 'Process Search', href: '/search', icon: Search },
    { name: 'Task Assignment', href: '/tasks', icon: Users },
    { name: 'Workflow Tracker', href: '/workflow', icon: BarChart3 },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-primary">
                🏛️ Bureaucracy Navigator
              </h1>
              {/* Backend Status Indicator */}
              <div className="ml-4 flex items-center">
                {backendStatus === 'connected' ? (
                  <div className="flex items-center text-green-600 text-sm">
                    <Wifi className="h-4 w-4 mr-1" />
                    Backend Connected
                  </div>
                ) : backendStatus === 'checking' ? (
                  <div className="flex items-center text-yellow-600 text-sm">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-yellow-600 mr-1"></div>
                    Checking...
                  </div>
                ) : (
                  <div className="flex items-center text-red-600 text-sm">
                    <WifiOff className="h-4 w-4 mr-1" />
                    Backend Offline
                  </div>
                )}
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              {navigation.map((item) => (
                <a
                  key={item.name}
                  href={item.href}
                  className="flex items-center px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:text-primary hover:bg-gray-50"
                >
                  <item.icon className="h-4 w-4 mr-2" />
                  {item.name}
                </a>
              ))}
              
              {user && (
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-600">
                    {user.name}
                  </span>
                  <button
                    onClick={logout}
                    className="flex items-center px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:text-danger hover:bg-gray-50"
                  >
                    <LogOut className="h-4 w-4" />
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {children}
      </main>
    </div>
  )
}

export default Layout
