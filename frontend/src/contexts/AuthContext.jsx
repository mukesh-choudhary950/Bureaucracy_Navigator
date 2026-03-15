import React, { createContext, useContext, useState } from 'react'
import axios from 'axios'

const AuthContext = createContext()

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    // Load user from localStorage on init
    const savedUser = localStorage.getItem('user')
    return savedUser ? JSON.parse(savedUser) : null
  })
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    return !!localStorage.getItem('user')
  })

  const login = async (credentials) => {
    try {
      // Call the real authentication API
      const response = await axios.post('http://localhost:8000/api/v1/auth/login', {
        name: credentials.name,
        password: credentials.password
      })
      
      if (response.data) {
        const userData = {
          id: response.data.id,
          name: response.data.name,
          email: response.data.email,
          phone: response.data.phone,
          role: credentials.role || 'manager',
          department: credentials.department || 'general'
        }
        setUser(userData)
        setIsAuthenticated(true)
        localStorage.setItem('user', JSON.stringify(userData))
        return { success: true, user: userData }
      }
    } catch (error) {
      console.error('Login error:', error)
      return { success: false, error: error.response?.data?.detail || 'Login failed' }
    }
  }

  const register = async (userData) => {
    try {
      const response = await axios.post('http://localhost:8000/api/v1/auth/register', {
        name: userData.name,
        phone: userData.phone,
        email: userData.email,
        password: userData.password
      })
      
      return { success: true, user: response.data }
    } catch (error) {
      console.error('Registration error:', error)
      return { success: false, error: error.response?.data?.detail || 'Registration failed' }
    }
  }

  const updateProfile = async (profileData) => {
    try {
      if (!user?.name) {
        return { success: false, error: 'No user logged in' }
      }

      const response = await axios.put(`http://localhost:8000/api/v1/auth/profile/${user.name}`, {
        name: profileData.name || user.name,
        phone: profileData.phone || user.phone,
        email: profileData.email || user.email,
        current_password: profileData.currentPassword,
        new_password: profileData.newPassword
      })

      if (response.data.success) {
        const updatedUser = {
          ...user,
          name: profileData.name || user.name,
          phone: profileData.phone || user.phone,
          email: profileData.email || user.email
        }
        setUser(updatedUser)
        localStorage.setItem('user', JSON.stringify(updatedUser))
        return { success: true, user: updatedUser }
      }
    } catch (error) {
      console.error('Profile update error:', error)
      return { success: false, error: error.response?.data?.detail || 'Failed to update profile' }
    }
  }

  const logout = () => {
    setUser(null)
    setIsAuthenticated(false)
    localStorage.removeItem('user')
  }

  const value = {
    user,
    isAuthenticated,
    isUser: !!user,
    login,
    register,
    logout,
    updateProfile
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}
