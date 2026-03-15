import React, { createContext, useContext, useState } from 'react'
import axios from 'axios'

const QueryContext = createContext()

export const useQuery = () => {
  const context = useContext(QueryContext)
  if (!context) {
    throw new Error('useQuery must be used within a QueryProvider')
  }
  return context
}

export const QueryProvider = ({ children }) => {
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState([])
  const [selectedProcess, setSelectedProcess] = useState(null)
  const [pdfsScanned, setPdfsScanned] = useState(false)

  const ensurePDFsScanned = async () => {
    if (!pdfsScanned) {
      try {
        // Scan PDFs in background without showing status to user
        await axios.post('http://localhost:8000/api/v1/query/scan-pdfs', {}, {
          timeout: 10000, // Reduced from 30s to 10s
          validateStatus: (status) => status < 500
        })
        setPdfsScanned(true)
      } catch (error) {
        console.log('PDF scanning failed, will proceed with available data:', error)
        // Don't block user query if PDF scanning fails
        setPdfsScanned(true) // Mark as scanned to prevent repeated attempts
      }
    }
  }

  const analyzeQuery = async (userQuery) => {
    setLoading(true)
    try {
      // Ensure PDFs are scanned before processing query
      await ensurePDFsScanned()
      
      // Try targeted summary from PDFs
      const summaryResponse = await axios.post('http://localhost:8000/api/v1/query/targeted-summary', {
        query: userQuery,
        max_results: 3
      }, {
        timeout: 8000, // Reduced from 15s to 8s
        validateStatus: (status) => status < 500
      })
      
      if (summaryResponse.data.success && summaryResponse.data.summary) {
        // Use targeted summary if successful - completely hide sources and preserve formatting
        const cleanedSummary = summaryResponse.data.summary
          .replace(/(?:from|source|document|file|pdf|From|Source|Document|File|PDF):\s*[^\n]+/gi, '')
          .replace(/\(cid:\d+\)/g, '') // Remove CID references from PDFs
          .replace(/\n{3,}/g, '\n\n')  // Normalize multiple newlines to double
          .trim()
        
        setResults([{
          question: userQuery,
          answer: cleanedSummary,
          sources: [], // Completely hide sources
          confidence: 0.95,
          type: 'document_analysis'
        }])
        
        const steps = extractProcessSteps(summaryResponse.data.summary)
        setSelectedProcess({
          query: userQuery,
          steps: steps,
          aiAnalysis: summaryResponse.data
        })
      } else {
        // Fallback to general RAG if targeted summary fails
        const response = await axios.post('http://localhost:8000/api/v1/query/ask-simple', {
          question: userQuery,
          max_results: 5
        }, {
          timeout: 5000, // Reduced from 10s to 5s
          validateStatus: (status) => status < 500
        })
        
        const cleanedAnswer = response.data.answer
          .replace(/(?:from|source|document|file|pdf|From|Source|Document|File|PDF):\s*[^\n]+/gi, '')
          .replace(/\(cid:\d+\)/g, '') // Remove CID references from PDFs
          .replace(/\n{3,}/g, '\n\n')  // Normalize multiple newlines
          .trim()
        
        setResults([{
          ...response.data,
          answer: cleanedAnswer,
          sources: [] // Completely hide sources
        }])
        
        const steps = extractProcessSteps(cleanedAnswer)
        setSelectedProcess({
          query: userQuery,
          steps: steps,
          aiAnalysis: response.data
        })
      }
    } catch (error) {
      console.error('Error analyzing query:', error)
      
      // More user-friendly error message based on error type
      let errorMessage = 'Unable to process your request at this time.'
      
      if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
        errorMessage = 'Request timed out. The backend may be busy or not responding.'
      } else if (error.code === 'ERR_NETWORK' || error.message?.includes('Network')) {
        errorMessage = 'Cannot connect to backend server. Please ensure the backend is running on http://localhost:8000'
      } else if (error.response?.status === 500) {
        errorMessage = 'Server error occurred. Please try again in a moment.'
      }
      
      // Fallback response when backend is unavailable
      const fallbackResponse = {
        question: userQuery,
        answer: `${errorMessage}

Please check:
1. Backend server is running (python -m uvicorn app.main:app --reload)
2. No firewall is blocking port 8000
3. Try again in a few moments

Original query: ${userQuery}`,
        sources: [],
        confidence: 0.1,
        error: true
      }
      
      setResults([fallbackResponse])
      setSelectedProcess({
        query: userQuery,
        steps: [{
          id: 1,
          title: "Service Unavailable",
          status: 'error'
        }],
        aiAnalysis: fallbackResponse
      })
    } finally {
      setLoading(false)
    }
  }

  const extractProcessSteps = (aiResponse) => {
    // Simple regex to extract numbered steps from AI response
    const stepPattern = /\d+\.\s*([^.\n]+)/g
    const matches = aiResponse.match(stepPattern)
    return matches ? matches.map((match, index) => ({
      id: index + 1,
      title: match[1].trim(),
      status: 'pending'
    })) : []
  }

  const scanPDFs = async () => {
    try {
      const response = await axios.post('http://localhost:8000/api/v1/query/scan-pdfs', {}, {
        timeout: 30000,
        validateStatus: (status) => status < 500
      })
      return response.data
    } catch (error) {
      console.error('Error scanning PDFs:', error)
      throw error
    }
  }

  const getPDFStatus = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/v1/query/pdf-status', {
        timeout: 10000,
        validateStatus: (status) => status < 500
      })
      return response.data
    } catch (error) {
      console.error('Error getting PDF status:', error)
      return { total_pdfs: 0, pdf_files: [], categories: {} }
    }
  }

  const value = {
    query,
    setQuery,
    loading,
    results,
    selectedProcess,
    analyzeQuery,
    setSelectedProcess,
    scanPDFs,
    getPDFStatus
  }

  return (
    <QueryContext.Provider value={value}>
      {children}
    </QueryContext.Provider>
  )
}
