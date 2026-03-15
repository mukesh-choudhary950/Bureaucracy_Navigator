import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { User, Lock, ArrowRight, Eye, EyeOff } from 'lucide-react'

const Login = () => {
  const [formData, setFormData] = useState({
    name: '',
    password: ''
  })
  const [errors, setErrors] = useState({})
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const navigate = useNavigate()
  const { login } = useAuth()

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
    // Clear error for this field when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }))
    }
  }

  const validateForm = () => {
    const newErrors = {}
    
    if (!formData.name || formData.name.length < 3) {
      newErrors.name = 'Name is required'
    }
    
    if (!formData.password) {
      newErrors.password = 'Password is required'
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!validateForm()) return
    
    setLoading(true)
    
    // Create abort controller for timeout
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 10000) // 10 second timeout
    
    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: formData.name,
          password: formData.password
        }),
        signal: controller.signal
      })
      
      clearTimeout(timeoutId)
      
      if (response.ok) {
        const user = await response.json()
        login(user)
        navigate('/dashboard')
      } else {
        const error = await response.json()
        setErrors({ submit: error.detail || 'Login failed' })
      }
    } catch (error) {
      if (error.name === 'AbortError') {
        setErrors({ submit: 'Request timed out. Please check if backend is running.' })
      } else {
        setErrors({ submit: 'Network error. Please check if backend is running on port 8000.' })
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div 
        className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 flex items-center justify-center p-4"
        style={{
          background: 'linear-gradient(135deg, #dbeafe 0%, #e9d5ff 50%, #fce7f3 100%)',
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '1rem'
        }}
      >
      <div className="max-w-md w-full">
        <div 
          className="bg-white/80 backdrop-blur-lg rounded-2xl shadow-xl p-8 border border-white/20"
          style={{
            background: 'rgba(255, 255, 255, 0.8)',
            backdropFilter: 'blur(16px)',
            WebkitBackdropFilter: 'blur(16px)',
            borderRadius: '1rem',
            boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
            padding: '2rem',
            border: '1px solid rgba(255, 255, 255, 0.2)'
          }}
        >
          <div className="text-center mb-8">
            <div 
              className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full mb-4"
              style={{
                background: 'linear-gradient(135deg, #3b82f6 0%, #9333ea 100%)',
                width: '4rem',
                height: '4rem',
                borderRadius: '50%',
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: '1rem'
              }}
            >
              <User className="w-8 h-8 text-white" style={{ color: 'white' }} />
            </div>
            <h1 
              className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent"
              style={{
                background: 'linear-gradient(135deg, #2563eb 0%, #7c3aed 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
                fontSize: '1.875rem',
                fontWeight: 'bold',
                marginBottom: '0.5rem'
              }}
            >
              Welcome Back
            </h1>
            <p className="text-gray-600 mt-2" style={{ color: '#4b5563', marginTop: '0.5rem' }}>Sign in to your account</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Username
              </label>
              <div className="relative">
                <User className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  className={`w-full pl-10 pr-4 py-3 rounded-xl border ${errors.name ? 'border-red-500' : 'border-gray-200'} bg-white/50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all`}
                  placeholder="Enter your username"
                />
              </div>
              {errors.name && <p className="text-red-500 text-sm mt-1">{errors.name}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                <input
                  type={showPassword ? "text" : "password"}
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  className={`w-full pl-10 pr-12 py-3 rounded-xl border ${errors.password ? 'border-red-500' : 'border-gray-200'} bg-white/50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all`}
                  placeholder="Enter your password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                >
                  {showPassword ? (
                    <EyeOff className="h-4 w-4 text-gray-400" />
                  ) : (
                    <Eye className="h-4 w-4 text-gray-400" />
                  )}
                </button>
              </div>
            </div>

            <div>
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-gradient-to-r from-blue-500 to-purple-500 text-white py-3 px-4 rounded-xl font-semibold hover:from-blue-600 hover:to-purple-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all transform hover:scale-[1.02]"
                style={{
                  background: 'linear-gradient(135deg, #3b82f6 0%, #9333ea 100%)',
                  color: 'white',
                  padding: '0.75rem 1rem',
                  borderRadius: '0.75rem',
                  fontWeight: '600',
                  width: '100%',
                  border: 'none',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  opacity: loading ? 0.5 : 1,
                  transition: 'all 0.2s ease-in-out'
                }}
              >
                {loading ? (
                  <div className="flex items-center justify-center">
                    <div 
                      className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"
                      style={{
                        border: '2px solid rgba(255, 255, 255, 0.3)',
                        borderTop: '2px solid white',
                        borderRadius: '50%',
                        width: '1.25rem',
                        height: '1.25rem'
                      }}
                    ></div>
                  </div>
                ) : (
                  <div className="flex items-center justify-center">
                    Sign In
                    <ArrowRight className="ml-2 w-5 h-5" />
                  </div>
                )}
              </button>
            </div>
          </form>

          <div className="mt-8 text-center">
            <div 
              className="inline-flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-purple-100 to-pink-100 rounded-xl border border-purple-200"
              style={{
                background: 'linear-gradient(135deg, #f3e8ff 0%, #fdf2f8 100%)',
                borderRadius: '0.75rem',
                border: '1px solid #e9d5ff',
                padding: '0.75rem 1.5rem'
              }}
            >
              <span style={{ color: '#6b7280', fontSize: '0.875rem' }}>
                Don't have an account?
              </span>
              <a 
                href="/register" 
                className="font-semibold hover:underline"
                style={{ 
                  color: '#9333ea',
                  textDecoration: 'none',
                  fontWeight: '600',
                  fontSize: '0.875rem',
                  transition: 'all 0.2s ease-in-out'
                }}
                onMouseEnter={(e) => {
                  e.target.style.color = '#7c3aed'
                  e.target.style.textDecoration = 'underline'
                }}
                onMouseLeave={(e) => {
                  e.target.style.color = '#9333ea'
                  e.target.style.textDecoration = 'none'
                }}
              >
                Sign Up →
              </a>
            </div>
          </div>

          </div>
      </div>
    </div>
  )
}

export default Login
