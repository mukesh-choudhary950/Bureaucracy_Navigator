import React from 'react'
import { NavLink, useLocation } from 'react-router-dom'
import { 
  Home, 
  Search, 
  CheckSquare, 
  GitBranch, 
  User, 
  LogOut,
  FileText,
  TrendingUp,
  Users,
  Clock,
  Settings
} from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'

const Sidebar = () => {
  const location = useLocation()
  const { user, logout } = useAuth()

  const menuItems = [
    {
      title: 'Dashboard',
      path: '/dashboard',
      icon: Home,
      color: 'from-blue-500 to-cyan-500'
    },
    {
      title: 'Process Search',
      path: '/process-search',
      icon: Search,
      color: 'from-purple-500 to-pink-500'
    },
    {
      title: 'Task Assignment',
      path: '/task-assignment',
      icon: CheckSquare,
      color: 'from-green-500 to-emerald-500'
    },
    {
      title: 'Workflow Tracker',
      path: '/workflow-tracker',
      icon: GitBranch,
      color: 'from-orange-500 to-red-500'
    },
    {
      title: 'Profile',
      path: '/profile',
      icon: Settings,
      color: 'from-gray-500 to-gray-700'
    }
  ]

  const isActive = (path) => {
    return location.pathname === path
  }

  return (
    <div className="w-64 h-screen bg-gradient-to-b from-indigo-900 via-purple-900 to-pink-900 text-white flex flex-col">
      {/* Header */}
      <div className="p-6 border-b border-white/10">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-r from-purple-400 to-pink-400 rounded-full flex items-center justify-center">
            <User className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="font-semibold text-white">{user?.name || 'User'}</h2>
            <p className="text-xs text-purple-200">Welcome back!</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4">
        <div className="space-y-2">
          {menuItems.map((item) => {
            const Icon = item.icon
            const active = isActive(item.path)
            
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={`group flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-200 ${
                  active 
                    ? 'bg-white/20 shadow-lg backdrop-blur-sm border border-white/20' 
                    : 'hover:bg-white/10 hover:translate-x-1'
                }`}
              >
                <div className={`w-8 h-8 rounded-lg bg-gradient-to-r ${item.color} flex items-center justify-center ${
                  active ? 'shadow-md' : 'group-hover:shadow-md'
                }`}>
                  <Icon className="w-4 h-4 text-white" />
                </div>
                <span className={`font-medium ${
                  active ? 'text-white' : 'text-purple-200 group-hover:text-white'
                }`}>
                  {item.title}
                </span>
              </NavLink>
            )
          })}
        </div>

        {/* Quick Stats */}
        <div className="mt-8 p-4 bg-white/5 rounded-xl border border-white/10">
          <h3 className="text-xs font-semibold text-purple-300 mb-3">QUICK STATS</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <TrendingUp className="w-4 h-4 text-green-400" />
                <span className="text-xs text-purple-200">Active Tasks</span>
              </div>
              <span className="text-xs font-semibold text-green-400">12</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Users className="w-4 h-4 text-blue-400" />
                <span className="text-xs text-purple-200">Workflows</span>
              </div>
              <span className="text-xs font-semibold text-blue-400">8</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Clock className="w-4 h-4 text-yellow-400" />
                <span className="text-xs text-purple-200">Pending</span>
              </div>
              <span className="text-xs font-semibold text-yellow-400">5</span>
            </div>
          </div>
        </div>
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-white/10">
        <button
          onClick={logout}
          className="w-full flex items-center space-x-3 px-4 py-3 rounded-xl bg-red-500/20 hover:bg-red-500/30 transition-all duration-200 group"
        >
          <LogOut className="w-5 h-5 text-red-400 group-hover:text-red-300" />
          <span className="font-medium text-red-400 group-hover:text-red-300">Logout</span>
        </button>
      </div>
    </div>
  )
}

export default Sidebar
