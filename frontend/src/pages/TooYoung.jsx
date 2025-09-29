import React from 'react'
import Footer from '../components/Footer.jsx'

const TooYoung = () => {
  return (
    <div style={{ 
      padding: '40px', 
      textAlign: 'center',
      maxWidth: '600px',
      margin: '0 auto'
    }}>
      <h1 style={{ color: '#f39c12', marginBottom: '20px' }}>
        🚫 Access Restricted
      </h1>
      
      <div style={{ 
        backgroundColor: '#f8f9fa', 
        padding: '30px', 
        borderRadius: '8px',
        border: '1px solid #dee2e6'
      }}>
        <h2 style={{ color: '#495057', marginBottom: '15px' }}>
          Sorry, you're too young for this poll!
        </h2>
        
        <p style={{ color: '#6c757d', fontSize: '16px', lineHeight: '1.6' }}>
          This Teen Poll is designed for young people born between 2007-2012. 
          You'll need to wait a bit longer to participate!
        </p>
        
        <div style={{ marginTop: '30px' }}>
          <button 
            onClick={() => window.history.back()}
            style={{
              padding: '12px 24px',
              backgroundColor: '#6c757d',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '16px'
            }}
          >
            ← Go Back
          </button>
        </div>
      </div>
      
      {/* Footer */}
      <Footer />
    </div>
  )
}

export default TooYoung
