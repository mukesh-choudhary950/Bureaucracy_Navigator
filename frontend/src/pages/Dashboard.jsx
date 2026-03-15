import React, { useState } from 'react'
import { useQuery } from '../contexts/QueryContext'
import { useAuth } from '../contexts/AuthContext'
import { Search, FileText, TrendingUp, Users, Clock, Send, Sparkles } from 'lucide-react'

const Dashboard = () => {
  const { user } = useAuth()
  const { analyzeQuery, loading, results, selectedProcess } = useQuery()
  const [customQuery, setCustomQuery] = useState('')

  const handleQuickQuery = async (query) => {
    try {
      await analyzeQuery(query)
    } catch (error) {
      console.error('Quick query failed:', error)
    }
  }

  const handleCustomQuery = async (e) => {
    e.preventDefault()
    if (customQuery.trim()) {
      await handleQuickQuery(customQuery)
    }
  }

  const commonQueries = [
    "What agriculture certificates are available?",
    "How to apply for business certificates?",
    "Land and property certificate process",
    "Vehicle and transport certificates",
    "Certificate requirements and documents"
  ]

  const stats = [
    { label: 'Processes Analyzed', value: '24', icon: TrendingUp, color: 'text-green-600' },
    { label: 'Tasks Assigned', value: '18', icon: Users, color: 'text-blue-600' },
    { label: 'Pending Approvals', value: '6', icon: Clock, color: 'text-yellow-600' },
    { label: 'Completed This Month', value: '12', icon: FileText, color: 'text-green-600' }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 p-8">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-lg rounded-2xl shadow-xl p-8 border border-white/20 mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2">
              Welcome back, {user?.name || 'Manager'}! 🎉
            </h1>
            <p className="text-gray-600">
              AI-powered bureaucracy navigation and workflow automation
            </p>
          </div>
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-500 rounded-xl flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-500">Ready to assist</p>
              <p className="text-xs text-green-600 font-semibold">● Online</p>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="bg-white/80 backdrop-blur-lg rounded-2xl p-6 border border-white/20 shadow-xl">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Search className="h-5 w-5 mr-2 text-purple-600" />
            Quick Process Analysis
          </h2>
          <div className="grid grid-cols-1 gap-3">
            {commonQueries.map((query) => (
              <button
                key={query}
                onClick={() => analyzeQuery(query)}
                className="text-left px-4 py-3 bg-gradient-to-r from-purple-50 to-pink-50 hover:from-purple-100 hover:to-pink-100 rounded-xl transition-all transform hover:scale-[1.02] border border-purple-200 hover:border-purple-300"
              >
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full mr-3"></div>
                  <span className="text-gray-700 font-medium">{query}</span>
                </div>
              </button>
            ))}
          </div>
        </div>

        <div className="bg-white/80 backdrop-blur-lg rounded-2xl p-6 border border-white/20 shadow-xl">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Send className="h-5 w-5 mr-2 text-purple-600" />
            Custom Query
          </h2>
          <form onSubmit={handleCustomQuery} className="space-y-4">
            <div className="flex space-x-3">
              <input
                type="text"
                value={customQuery}
                onChange={(e) => setCustomQuery(e.target.value)}
                placeholder="Ask about any government process..."
                className="flex-1 px-4 py-3 rounded-xl border border-purple-200 bg-white/50 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
              />
              <button
                type="submit"
                disabled={loading || !customQuery.trim()}
                className="px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-xl font-semibold hover:from-purple-600 hover:to-pink-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all transform hover:scale-[1.02] shadow-lg"
              >
                {loading ? (
                  <div className="flex items-center">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    <span className="ml-2">Analyzing...</span>
                  </div>
                ) : (
                  <div className="flex items-center">
                    <Send className="w-5 h-5 mr-2" />
                    <span>Analyze</span>
                  </div>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>

      {/* Results Section */}
      {results && results.length > 0 && (
        <div className="bg-white/80 backdrop-blur-lg rounded-2xl p-8 border border-white/20 shadow-xl">
          <h2 className="text-xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent mb-6 flex items-center">
            <Sparkles className="w-6 h-6 mr-2" />
            Analysis Results
          </h2>
          <div className="space-y-6">
            {results.map((result, index) => (
              <div key={index} className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl p-6 border border-purple-200">
                <div className="flex items-start justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">{result.question}</h3>
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                    <span className="text-sm font-medium text-green-600">
                      {result.confidence ? `${Math.round(result.confidence * 100)}% Confidence` : 'Processed'}
                    </span>
                  </div>
                </div>
                <div className="prose prose-purple max-w-none">
                  <div className="whitespace-pre-wrap text-gray-700 leading-relaxed">
                    {result.answer}
                  </div>
                </div>
                {result.sources && result.sources.length > 0 && (
                  <div className="mt-4 pt-4 border-t border-purple-200">
                    <h4 className="text-sm font-semibold text-purple-600 mb-2">Sources:</h4>
                    <div className="space-y-1">
                      {result.sources.map((source, idx) => (
                        <div key={idx} className="text-xs text-purple-500 bg-purple-50 px-2 py-1 rounded">
                          {source.filename || `Source ${idx + 1}`}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="bg-white/80 backdrop-blur-lg rounded-2xl p-12 border border-white/20 shadow-xl text-center">
          <div className="flex flex-col items-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-4 border-purple-500 mb-4"></div>
            <div>
              <h3 className="text-lg font-semibold text-purple-600 mb-2">Analyzing your query...</h3>
              <p className="text-gray-600">Processing documents and generating insights</p>
            </div>
          </div>
        </div>
      )}

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => (
          <div key={stat.label} className="bg-white rounded-lg shadow p-6">
            <div className={`flex items-center ${stat.color}`}>
              <stat.icon className="h-8 w-8 mr-3" />
              <div>
                <p className="text-sm font-medium text-gray-600">{stat.label}</p>
                <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Analysis Results */}
      {results.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            AI Analysis Results
          </h2>
          <div className="space-y-4">
            {results.map((result, index) => (
              <div key={index} className="border-l-4 border-primary pl-4">
                <div className="font-medium text-gray-900 mb-2">
                  Query: {result.question}
                </div>
                <div className="text-sm text-gray-700 mb-3 whitespace-pre-wrap">
                  {result.answer}
                </div>
                {result.sources && result.sources.length > 0 && (
                  <div className="text-xs text-gray-500">
                    <strong>Sources:</strong> {result.sources.length} documents referenced
                  </div>
                )}
                {result.confidence && (
                  <div className="text-xs text-gray-500 mt-1">
                    <strong>Confidence:</strong> {Math.round(result.confidence * 100)}%
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {selectedProcess && selectedProcess.steps && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Process Steps: {selectedProcess.query}
          </h2>
          <div className="space-y-3">
            {selectedProcess.steps.map((step, index) => (
              <div key={step.id} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                <div className="flex-shrink-0 w-8 h-8 bg-primary text-white rounded-full flex items-center justify-center text-sm font-medium">
                  {index + 1}
                </div>
                <div className="flex-1">
                  <div className="font-medium text-gray-900">{step.title}</div>
                  <div className="text-sm text-gray-500">Status: {step.status}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent Activity */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Recent AI Analysis
        </h2>
        <div className="space-y-3">
          <div className="border-l-4 border-primary pl-4">
            <div className="font-medium text-gray-900">Food Business License Process</div>
            <div className="text-sm text-gray-600">
              AI identified 7 steps including FSSAI license, GST registration, and local permits
            </div>
            <div className="text-xs text-gray-500 mt-1">2 hours ago</div>
          </div>
          <div className="border-l-4 border-warning pl-4">
            <div className="font-medium text-gray-900">Restaurant Permit Application</div>
            <div className="text-sm text-gray-600">
              5-step process with municipal compliance requirements
            </div>
            <div className="text-xs text-gray-500 mt-1">5 hours ago</div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
