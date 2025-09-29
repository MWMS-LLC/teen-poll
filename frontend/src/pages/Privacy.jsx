import React from 'react'
import { useNavigate } from 'react-router-dom'
import HamburgerMenu from '../components/HamburgerMenu.jsx'
import Footer from '../components/Footer.jsx'

const Privacy = () => {
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
        <h1 style={styles.pageTitle}>Privacy Policy</h1>
      </div>

      {/* Content Section */}
      <div style={styles.contentSection}>
        <div style={styles.section}>
          <p style={styles.text}>
            We do not knowingly collect any personal information, including name, email, or any other personal information, from anyone.
          </p>
          <p style={styles.text}>
            However, our app targets teens. If you are under 13, please do not use this app. If you believe a child under 13 has provided us with information, please contact us and we will promptly delete it.
          </p>
          <p style={styles.text}>
            If you have any questions about this policy, please contact us at{' '}
            <a href="mailto:info@myworldmysay.com" style={styles.emailLink}>
              info@myworldmysay.com
            </a>
          </p>
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
    margin: '0 0 20px 0'
  },
  
  dateText: {
    color: 'rgba(255, 255, 255, 0.7)',
    fontSize: '14px',
    fontStyle: 'italic',
    margin: '0 0 20px 0'
  },
  
  emailLink: {
    color: '#4ECDC4',
    textDecoration: 'underline'
  }
}

export default Privacy
