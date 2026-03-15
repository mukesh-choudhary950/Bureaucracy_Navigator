import React, { useState } from 'react'
import { useQuery } from '../contexts/QueryContext'
import { Search, FileText, Clock, CheckCircle, AlertCircle } from 'lucide-react'

const ProcessSearch = () => {
  const { query, setQuery, analyzeQuery, loading, results } = useQuery()
  const [searchInput, setSearchInput] = useState('')

  const handleSearch = () => {
    if (searchInput.trim()) {
      analyzeQuery(searchInput)
    }
  }

  return (
    <div className="space-y-6">
      {/* Search Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">
          Government Process Search 🔍
        </h1>
        <p className="text-gray-600 mb-6">
          Ask AI about any government process, license, or permit
        </p>
        
        {/* Search Input */}
        <div className="flex space-x-4">
          <input
            type="text"
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            placeholder="e.g., How to apply for business license?"
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-primary focus:border-primary"
          />
          <button
            onClick={handleSearch}
            disabled={loading}
            className="px-6 py-3 bg-primary text-white rounded-lg hover:bg-primary-dark disabled:opacity-50 flex items-center"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Analyzing...
              </>
            ) : (
              <>
                <Search className="h-5 w-5 mr-2" />
                Analyze Process
              </>
            )}
          </button>
        </div>
      </div>

      {/* AI Results */}
      {results.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            {results[0].error ? '🔌 Backend Connection Issue' : '🤖 AI Analysis Results'}
          </h2>
          
          {results.map((result, index) => (
            <div key={index} className={`border-l-4 ${result.error ? 'border-red-500' : 'border-primary'} pl-6 mb-6`}>
              {/* Question */}
              <div className={`p-4 rounded-t-lg ${result.error ? 'bg-red-50' : 'bg-gray-50'}`}>
                <div className="flex items-center mb-2">
                  <FileText className="h-5 w-5 mr-2" />
                  <h3 className="font-semibold text-lg text-gray-900">
                    {result.question}
                  </h3>
                </div>
              </div>
              
              {/* AI Answer */}
              <div className="p-4">
                <div className="flex items-center mb-3">
                  {result.error ? (
                    <AlertCircle className="h-5 w-5 mr-2 text-red-500" />
                  ) : (
                    <CheckCircle className="h-5 w-5 mr-2 text-green-500" />
                  )}
                  <span className={`font-medium ${result.error ? 'text-red-700' : 'text-green-700'}`}>
                    {result.error ? 'Connection Error' : 'AI Recommendation'}
                  </span>
                </div>
                <div className={`prose prose-sm max-w-none whitespace-pre-wrap ${result.error ? 'text-red-700' : 'text-gray-700'}`}>
                  {result.answer}
                </div>
              </div>
              
              {/* Error Actions */}
              {result.error && (
                <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
                  <h4 className="font-medium text-orange-900 mb-3">🔧 Troubleshooting Steps:</h4>
                  <div className="space-y-2 text-sm text-gray-700">
                    <div>1. <strong>Check Backend:</strong> Ensure backend is running on http://localhost:8000</div>
                    <div>2. <strong>Verify API Key:</strong> Check your Groq API key in .env file</div>
                    <div>3. <strong>Test Connection:</strong> Try: <code className="bg-gray-100 px-2 py-1 rounded">curl http://localhost:8000/health</code></div>
                    <div>4. <strong>Check Logs:</strong> Look for backend error messages</div>
                  </div>
                  <div className="flex space-x-3 mt-4">
                    <button 
                      onClick={() => window.location.reload()}
                      className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                    >
                      Retry Connection
                    </button>
                    <button 
                      onClick={() => window.open('http://localhost:8000/docs', '_blank')}
                      className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
                    >
                      Open API Docs
                    </button>
                  </div>
                </div>
              )}
              
              {/* Sources */}
              {!result.error && result.sources && result.sources.length > 0 && (
                <div className="bg-blue-50 p-4 rounded-b-lg">
                  <div className="flex items-center mb-2">
                    <AlertCircle className="h-5 w-5 mr-2 text-blue-500" />
                    <span className="font-medium text-blue-700">Information Sources</span>
                  </div>
                  <div className="space-y-2">
                    {result.sources.map((source, idx) => (
                      <div key={idx} className="text-sm text-gray-600">
                        <span className="font-medium">Source {idx + 1}:</span> {source.filename || 'Government Database'}
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Confidence */}
              <div className="mt-3 pt-3 border-t">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">Confidence Score</span>
                  <span className={`text-sm font-medium ${
                    result.confidence > 0.8 ? 'text-green-600' : 
                    result.confidence > 0.6 ? 'text-yellow-600' : 'text-red-600'
                  }`}>
                    {Math.round(result.confidence * 100)}%
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* No Results State */}
      {!loading && results.length === 0 && query && (
        <div className="bg-white rounded-lg shadow p-6 text-center">
          <div className="animate-pulse">
            <div className="h-8 w-8 bg-primary rounded-full mx-auto mb-4"></div>
            <p className="text-gray-600">AI is analyzing your query...</p>
          </div>
        </div>
      )}

      {/* Empty State */}
      {!loading && results.length === 0 && !query && (
        <div className="bg-white rounded-lg shadow p-6 text-center">
          <Search className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Start Your Search
          </h3>
          <p className="text-gray-600">
            Enter a government process or question above to get AI-powered guidance
          </p>
        </div>
      )}
    </div>
  )
}

export default ProcessSearch
