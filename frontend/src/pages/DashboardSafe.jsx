import React, { useState } from 'react'
import { useQuery } from '../contexts/QueryContext'
import { useAuth } from '../contexts/AuthContext'
import { Search, Send, Sparkles } from 'lucide-react'

const DashboardSafe = () => {
  const { user } = useAuth()
  const { analyzeQuery, loading, results } = useQuery()
  const [customQuery, setCustomQuery] = useState('')
  const [clickedQuery, setClickedQuery] = useState(null)

  const handleQuickQuery = async (query) => {
    setCustomQuery(query)
    setClickedQuery(query)
    try {
      await analyzeQuery(query)
    } catch (error) {
      console.error('Query failed:', error)
    }
  }

  const handleCustomQuery = async (e) => {
    e.preventDefault()
    if (customQuery.trim()) {
      try {
        await analyzeQuery(customQuery)
      } catch (error) {
        console.error('Query failed:', error)
      }
    }
  }

  const commonQueries = [
    "How to apply for Aadhaar card?",
    "Birth certificate application process",
    "Death certificate application guide",
    "Income certificate application",
    "Land ownership certificate process",
    "Land transfer procedure",
    "Ration card application guide",
    "Agriculture certificates in Telangana",
    "Business industry certificates",
    "Vehicle transport certificates"
  ]

  return (
    <div style={{ padding: '2rem', minHeight: '100vh' }}>
      {/* Header */}
      <div style={{
        background: 'rgba(255, 255, 255, 0.8)',
        backdropFilter: 'blur(16px)',
        borderRadius: '1rem',
        padding: '2rem',
        marginBottom: '2rem',
        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)'
      }}>
        <h1 style={{
          background: 'linear-gradient(135deg, #3b82f6 0%, #9333ea 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text',
          fontSize: '2rem',
          fontWeight: 'bold',
          marginBottom: '0.5rem'
        }}>
          Welcome back, {user?.name || 'Manager'}! 🎉
        </h1>
        <p style={{ color: '#6b7280' }}>
          AI-powered bureaucracy navigation and workflow automation
        </p>
      </div>

      {/* Quick Actions */}
      <div style={{
        background: 'rgba(255, 255, 255, 0.8)',
        backdropFilter: 'blur(16px)',
        borderRadius: '1rem',
        padding: '2rem',
        marginBottom: '2rem',
        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)'
      }}>
        <h2 style={{ color: '#1f2937', marginBottom: '1rem' }}>Quick Process Analysis</h2>
        <div style={{ display: 'grid', gap: '1rem' }}>
          {commonQueries.map((query, index) => (
            <button
              key={index}
              onClick={() => handleQuickQuery(query)}
              onMouseEnter={(e) => {
                if (clickedQuery !== query) {
                  e.target.style.background = 'linear-gradient(135deg, #e9d5ff 0%, #fce7f3 100%)'
                  e.target.style.transform = 'scale(1.01)'
                }
              }}
              onMouseLeave={(e) => {
                if (clickedQuery !== query) {
                  e.target.style.background = 'linear-gradient(135deg, #f3e8ff 0%, #fdf2f8 100%)'
                  e.target.style.transform = 'scale(1)'
                }
              }}
              style={{
                background: clickedQuery === query 
                  ? 'linear-gradient(135deg, #ddd6fe 0%, #fce7f3 100%)'
                  : 'linear-gradient(135deg, #f3e8ff 0%, #fdf2f8 100%)',
                border: clickedQuery === query 
                  ? '2px solid #9333ea' 
                  : '1px solid #e9d5ff',
                borderRadius: '0.75rem',
                padding: '1rem',
                textAlign: 'left',
                cursor: 'pointer',
                transition: 'all 0.2s ease-in-out',
                transform: clickedQuery === query ? 'scale(1.02)' : 'scale(1)',
                boxShadow: clickedQuery === query 
                  ? '0 4px 6px -1px rgba(147, 51, 234, 0.3)' 
                  : 'none'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{ display: 'flex', alignItems: 'center' }}>
                  <div style={{
                    width: '0.5rem',
                    height: '0.5rem',
                    background: clickedQuery === query 
                      ? 'linear-gradient(135deg, #9333ea 0%, #ec4899 100%)'
                      : 'linear-gradient(135deg, #3b82f6 0%, #9333ea 100%)',
                    borderRadius: '50%',
                    marginRight: '0.75rem',
                    animation: clickedQuery === query ? 'pulse 2s infinite' : 'none'
                  }}></div>
                  <span style={{ 
                    color: clickedQuery === query ? '#6b21a8' : '#374151', 
                    fontWeight: clickedQuery === query ? '600' : '500' 
                  }}>
                    {query}
                  </span>
                </div>
                {clickedQuery === query && (
                  <div style={{
                    color: '#9333ea',
                    fontSize: '0.875rem',
                    fontWeight: '600',
                    display: 'flex',
                    alignItems: 'center'
                  }}>
                    ✓ Clicked
                  </div>
                )}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Custom Query */}
      <div style={{
        background: 'rgba(255, 255, 255, 0.8)',
        backdropFilter: 'blur(16px)',
        borderRadius: '1rem',
        padding: '2rem',
        marginBottom: '2rem',
        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)'
      }}>
        <h2 style={{ color: '#1f2937', marginBottom: '1rem' }}>Custom Query</h2>
        <form onSubmit={handleCustomQuery} style={{ display: 'flex', gap: '1rem' }}>
          <input
            type="text"
            value={customQuery}
            onChange={(e) => setCustomQuery(e.target.value)}
            placeholder="Ask about any government process..."
            style={{
              flex: 1,
              padding: '0.75rem 1rem',
              borderRadius: '0.75rem',
              border: '1px solid #e9d5ff',
              background: 'rgba(255, 255, 255, 0.5)',
              fontSize: '1rem'
            }}
          />
          <button
            type="submit"
            disabled={loading || !customQuery.trim()}
            style={{
              background: 'linear-gradient(135deg, #3b82f6 0%, #9333ea 100%)',
              color: 'white',
              padding: '0.75rem 1.5rem',
              borderRadius: '0.75rem',
              fontWeight: '600',
              border: 'none',
              cursor: loading || !customQuery.trim() ? 'not-allowed' : 'pointer',
              opacity: loading || !customQuery.trim() ? 0.5 : 1,
              transition: 'all 0.2s ease-in-out'
            }}
          >
            {loading ? 'Analyzing...' : 'Analyze'}
          </button>
        </form>
      </div>

      {/* Results */}
      {results && results.length > 0 && (
        <div style={{
          background: 'rgba(255, 255, 255, 0.8)',
          backdropFilter: 'blur(16px)',
          borderRadius: '1rem',
          padding: '2rem',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)'
        }}>
          <h2 style={{ 
            background: 'linear-gradient(135deg, #3b82f6 0%, #9333ea 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
            marginBottom: '1.5rem'
          }}>
            Analysis Results
          </h2>
          {results.map((result, index) => (
            <div key={index} style={{
              background: 'linear-gradient(135deg, #f3e8ff 0%, #fdf2f8 100%)',
              border: '1px solid #e9d5ff',
              borderRadius: '0.75rem',
              padding: '1.5rem',
              marginBottom: '1rem'
            }}>
              <h3 style={{ color: '#1f2937', marginBottom: '1rem' }}>{result.question}</h3>
              <div style={{ 
                color: '#374151', 
                lineHeight: '1.6',
                whiteSpace: 'pre-wrap',
                wordWrap: 'break-word'
              }}>
                {result.answer}
              </div>
              {/* Sources are hidden for cleaner interface */}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default DashboardSafe
