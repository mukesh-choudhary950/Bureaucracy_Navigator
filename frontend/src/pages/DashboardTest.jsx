import React from 'react'

const DashboardTest = () => {
  return (
    <div style={{ padding: '2rem' }}>
      <h1 style={{ color: '#1f2937', fontSize: '2rem', marginBottom: '1rem' }}>
        Dashboard Loaded Successfully! 🎉
      </h1>
      <p style={{ color: '#6b7280', fontSize: '1.1rem' }}>
        If you can see this message, the routing is working correctly.
      </p>
      <div style={{ 
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        padding: '1rem',
        borderRadius: '0.5rem',
        marginTop: '1rem'
      }}>
        Test Card Component
      </div>
    </div>
  )
}

export default DashboardTest
