import React from 'react'
import { useNavigate } from 'react-router-dom'
import HamburgerMenu from '../components/HamburgerMenu.jsx'
import Footer from '../components/Footer.jsx'

const Contact = () => {
  const navigate = useNavigate()

  return (
    <div style={styles.container}>
      {/* Hamburger Menu */}
      <HamburgerMenu />
      
      {/* Header Section */}
      <div style={styles.headerSection}>
        <div style={styles.backButton} onClick={() => navigate('/')}>
          ← Back
        </div>
        <h1 style={styles.pageTitle}>Contact Us</h1>
      </div>

      {/* Content Section */}
      <div style={styles.contentSection}>
        <div style={styles.section}>
          <p style={styles.text}>
            If you have questions, feedback, or need support, please email us at:
          </p>
          <a href="mailto:info@myworldmysay.com" style={styles.emailLink}>
            info@myworldmysay.com
          </a>
        </div>
      </div>

      {/* Footer */}
      <Footer />
    </div>
  )
}

const styles = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    background: 'linear-gradient(135deg, #0A0F2B 0%, #1A1F3B 50%, #2A2F4B 100%)',
    position: 'relative',
    overflowY: 'auto',
    padding: '20px'
  },
  
  headerSection: {
    marginTop: '60px',
    marginBottom: '30px',
    textAlign: 'center',
    width: '100%',
    maxWidth: '800px'
  },
  
  backButton: {
    color: 'rgba(255, 255, 255, 0.7)',
    fontSize: '16px',
    cursor: 'pointer',
    marginBottom: '20px',
    transition: 'all 0.2s ease',
    display: 'inline-block',
    padding: '8px 16px',
    borderRadius: '20px',
    background: 'rgba(255, 255, 255, 0.1)',
    border: '1px solid rgba(255, 255, 255, 0.2)',
    alignSelf: 'flex-start'
  },
  
  pageTitle: {
    fontSize: '36px',
    fontWeight: 'bold',
    color: 'white',
    marginBottom: '15px',
    textShadow: '0 0 20px rgba(255, 255, 255, 0.3)'
  },
  
  contentSection: {
    width: '100%',
    maxWidth: '800px',
    display: 'flex',
    flexDirection: 'column',
    gap: '25px',
    marginBottom: '40px'
  },
  
  section: {
    background: 'rgba(255, 255, 255, 0.05)',
    borderRadius: '16px',
    padding: '25px',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    backdropFilter: 'blur(10px)'
  },
  
  sectionTitle: {
    fontSize: '20px',
    fontWeight: '600',
    color: 'white',
    marginBottom: '15px'
  },
  
  text: {
    color: 'rgba(255, 255, 255, 0.9)',
    fontSize: '16px',
    lineHeight: '1.6',
    margin: 0
  },
  
  contactMethods: {
    display: 'flex',
    flexDirection: 'column',
    gap: '20px'
  },
  
  contactMethod: {
    display: 'flex',
    alignItems: 'center',
    gap: '15px'
  },
  
  icon: {
    fontSize: '24px',
    flexShrink: 0
  },
  
  methodTitle: {
    fontSize: '18px',
    fontWeight: '600',
    color: 'white',
    marginBottom: '5px'
  },
  
  methodText: {
    color: 'rgba(255, 255, 255, 0.8)',
    fontSize: '14px',
    margin: 0
  },
  
  helpList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px'
  },
  
  helpItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    color: 'rgba(255, 255, 255, 0.9)',
    fontSize: '16px'
  },
  
  bullet: {
    color: '#4ECDC4',
    fontSize: '18px',
    fontWeight: 'bold'
  }
}

export default Contact
