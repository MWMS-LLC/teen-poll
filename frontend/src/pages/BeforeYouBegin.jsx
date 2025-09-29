import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import HamburgerMenu from '../components/HamburgerMenu.jsx'
import Footer from '../components/Footer.jsx'

const BeforeYouBegin = () => {
  const navigate = useNavigate()


  return (
    <div style={styles.container}>
      {/* Hamburger Menu */}
      <HamburgerMenu />
      
      {/* Header Section */}
      <div style={styles.headerSection}>
        <h1 style={styles.pageTitle}>Before You Begin</h1>
      </div>

      {/* Warning Box */}
      <div style={styles.warningBox}>
        <span style={styles.warningIcon}>⚠️</span>
        <span style={styles.warningText}>(Please read before selecting a bubble)</span>
      </div>

      {/* Content Sections */}
      <div style={styles.contentContainer}>
        <div style={styles.section}>
          <h2 style={styles.sectionTitle}>What this is:</h2>
          <ul style={styles.bulletList}>
            <li>A place to explore questions about life, emotions, and identity</li>
            <li>A space to hear how others feel, and add your say</li>
            <li>Messages that respond to your answers—always with care</li>
          </ul>
        </div>

        <div style={styles.section}>
          <h2 style={styles.sectionTitle}>What this is not:</h2>
          <ul style={styles.bulletList}>
            <li>It's not therapy or medical advice</li>
            <li>It's not a place for emergencies or crisis help</li>
            <li>It's not collecting your personal info—we don't ask your name, email, or track you</li>
          </ul>
        </div>

        <div style={styles.section}>
          <h2 style={styles.sectionTitle}>If you're ever feeling overwhelmed:</h2>
          <p style={styles.overwhelmedText}>
            You can find a therapist or psychiatrist <button 
              style={styles.helpLink}
              onClick={() => navigate('/help')}
            >
              here
            </button> → (links to Help & Resources page)
          </p>
          <p style={styles.emergencyText}>
            Or, in an emergency, please call 911 or talk to a trusted adult.
          </p>
        </div>

        <div style={styles.section}>
          <h2 style={styles.sectionTitle}>User-Submitted Text Responses</h2>
          <p style={styles.overwhelmedText}>
            Some parts of this app allow users to submit short, free-form responses (e.g., "Other" options). These entries are not monitored, moderated, or reviewed in real time, and are not intended for communication of sensitive, personal, or emergency-related information.
          </p>
          <p style={styles.overwhelmedText}>
            By using this app, you understand and agree that we are not responsible for reviewing, acting upon, or responding to any user-submitted text.
          </p>
          <p style={styles.emergencyText}>
            If you are in danger or need help, please contact a trusted adult, counselor, or crisis resource immediately. This app does not provide medical, psychological, or emergency support.
          </p>
        </div>
      </div>

      {/* Back Button */}
      <div style={styles.buttonContainer}>
        <button 
          style={styles.backButton}
          onClick={() => navigate('/')}
        >
          ← Go Back
        </button>
      </div>
      
      {/* Footer */}
      <Footer />
    </div>
  )
}

// Premium styling
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
  
  pageTitle: {
    fontSize: '36px',
    fontWeight: 'bold',
    color: 'white',
    marginBottom: '15px',
    textShadow: '0 0 20px rgba(255, 255, 255, 0.3)'
  },
  
  warningBox: {
    background: '#FF4444',
    color: 'white',
    padding: '15px 20px',
    borderRadius: '8px',
    marginBottom: '30px',
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    maxWidth: '800px',
    width: '100%'
  },
  
  warningIcon: {
    fontSize: '20px'
  },
  
  warningText: {
    fontSize: '16px',
    fontWeight: '500'
  },
  
  contentContainer: {
    width: '100%',
    maxWidth: '800px',
    display: 'flex',
    flexDirection: 'column',
    gap: '30px',
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
  
  bulletList: {
    color: 'rgba(255, 255, 255, 0.9)',
    fontSize: '16px',
    lineHeight: '1.6',
    paddingLeft: '20px'
  },
  
  overwhelmedText: {
    color: 'rgba(255, 255, 255, 0.9)',
    fontSize: '16px',
    lineHeight: '1.6',
    marginBottom: '15px'
  },
  
  helpLink: {
    background: 'none',
    border: 'none',
    color: '#4ECDC4',
    textDecoration: 'underline',
    cursor: 'pointer',
    fontSize: '16px',
    fontFamily: 'inherit'
  },
  
  emergencyText: {
    color: 'rgba(255, 255, 255, 0.9)',
    fontSize: '16px',
    lineHeight: '1.6',
    fontWeight: '500'
  },
  
  buttonContainer: {
    marginTop: '20px'
  },
  
  backButton: {
    background: 'rgba(255, 255, 255, 0.1)',
    color: 'white',
    border: '1px solid rgba(255, 255, 255, 0.2)',
    padding: '12px 24px',
    borderRadius: '25px',
    fontSize: '16px',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    fontFamily: 'inherit'
  }
}

export default BeforeYouBegin
