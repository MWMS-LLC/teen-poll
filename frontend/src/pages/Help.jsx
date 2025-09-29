import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import HamburgerMenu from '../components/HamburgerMenu.jsx'
import Footer from '../components/Footer.jsx'

const Help = () => {
  const navigate = useNavigate()


  return (
    <div style={styles.container}>
      {/* Hamburger Menu */}
      <HamburgerMenu />
      
      {/* Header Section */}
      <div style={styles.headerSection}>
        <div style={styles.backButton} onClick={() => navigate('/')}>
          ← Back to Home
        </div>
        <h1 style={styles.pageTitle}>Need to Talk to Someone?</h1>
        <div style={styles.pageSubtitle}>
          Here are two national directories that can help:
        </div>
      </div>

      {/* Directory Listings */}
      <div style={styles.directoryContainer}>
        <div style={styles.directoryCard}>
          <div style={styles.linkIcon}>🔗</div>
          <div>
            <a 
              href="https://www.aacap.org/AACAP/Families_Youth/CAP_Finder/AACAP/Families_and_Youth/Resources/CAP_Finder.aspx?hkey=61c4e311-beb7-4a25-ae4f-1ec61baf348c" 
              target="_blank" 
              rel="noopener noreferrer"
              style={styles.directoryLink}
            >
              Find a Teen Psychiatrist - AACAP
            </a>
            <p style={styles.directoryDescription}>From the American Academy of Child & Adolescent Psychiatry.</p>
            <p style={styles.disclaimer}>We don't endorse individual providers.</p>
          </div>
        </div>
        
        <div style={styles.directoryCard}>
          <div style={styles.linkIcon}>🔗</div>
          <div>
            <a 
              href="https://www.psychologytoday.com/us/therapists" 
              target="_blank" 
              rel="noopener noreferrer"
              style={styles.directoryLink}
            >
              Find a Therapist - Psychology Today
            </a>
            <p style={styles.directoryDescription}>Search by location, insurance, or specialty.</p>
            <p style={styles.disclaimer}>No endorsements implied.</p>
          </div>
        </div>
      </div>

      {/* More Support & Education */}
      <div style={styles.supportSection}>
        <h2 style={styles.supportTitle}>More Support & Education</h2>
        
        <div style={styles.supportContainer}>
          <div style={styles.supportCard}>
            <div style={styles.supportIcon}>📚</div>
            <div>
              <a 
                href="https://www.aacap.org/AACAP/Families_and_Youth/Resource_Centers/Home.aspx" 
                target="_blank" 
                rel="noopener noreferrer"
                style={styles.directoryLink}
              >
                AACAP Family & Youth Resources
              </a>
              <p style={styles.supportDescription}>
                Helpful guides for parents, teens, and kids on mental health and development.
              </p>
            </div>
          </div>
          
          <div style={styles.supportCard}>
            <div style={styles.supportIcon}>🚫</div>
            <div>
              <a 
                href="https://www.stopbullying.gov/get-help-now" 
                target="_blank" 
                rel="noopener noreferrer"
                style={styles.directoryLink}
              >
                StopBullying.gov - Get Help Now
              </a>
              <p style={styles.supportDescription}>
                If you or someone you know is being bullied, this site shows what you can do—and who can help.
              </p>
            </div>
          </div>
        </div>

        {/* Warning Box */}
        <div style={styles.warningBox}>
          <p style={styles.warningText}>
            This app is here to support reflection—not replace professional help. If you're ever in danger or crisis, please contact a trusted adult or call 911.
          </p>
        </div>
      </div>

      {/* Sources & Real-World Stats */}
      <div style={styles.sourcesSection}>
        <h2 style={styles.sourcesTitle}>
          <span style={styles.chartIcon}>📊</span>
          Sources & Real-World Stats
        </h2>
        <p style={styles.sourcesIntro}>
          Some of the questions in this app are inspired by real studies, articles, and stats. Here are a few we found helpful.
        </p>
        
        <div style={styles.statsList}>
          <div style={styles.statItem}>
            <span style={styles.statText}>Only 51% of high schoolers feel a sense of belonging → </span>
            <a 
              href="https://www.qualtrics.com/news/only-half-of-high-school-students-feel-a-sense-of-belonging-at-their-school-qualtrics-research-shows/" 
              target="_blank" 
              rel="noopener noreferrer"
              style={styles.statLink}
            >
              Qualtrics Study
            </a>
          </div>
          
          <div style={styles.statItem}>
            <span style={styles.statText}>Teen loneliness doubled from 2012-2018 → </span>
            <a 
              href="https://www.snexplores.org/article/teens-feels-lonely-school-cell-phones-internet" 
              target="_blank" 
              rel="noopener noreferrer"
              style={styles.statLink}
            >
              Science News for Students
            </a>
          </div>
          
          <div style={styles.statItem}>
            <span style={styles.statText}>19.2% of students report being bullied → </span>
            <a 
              href="https://www.stopbullying.gov/resources/facts#fast-facts" 
              target="_blank" 
              rel="noopener noreferrer"
              style={styles.statLink}
            >
              StopBullying.gov
            </a>
          </div>
          
          <div style={styles.statItem}>
            <span style={styles.statText}>What to do about bullying → </span>
            <a 
              href="https://www.stopbullying.gov/resources/teens" 
              target="_blank" 
              rel="noopener noreferrer"
              style={styles.statLink}
            >
              StopBullying.gov Teen Guide
            </a>
          </div>
          
          <div style={styles.statItem}>
            <span style={styles.statText}>More than 40% of college grads are underemployed → </span>
            <a 
              href="https://www.wsj.com/lifestyle/careers/college-degree-jobs-unused-440b2abd" 
              target="_blank" 
              rel="noopener noreferrer"
              style={styles.statLink}
            >
              Wall Street Journal
            </a>
          </div>
        </div>
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
    marginBottom: '40px',
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
    border: '1px solid rgba(255, 255, 255, 0.2)'
  },
  
  pageTitle: {
    fontSize: '36px',
    fontWeight: 'bold',
    color: 'white',
    marginBottom: '15px',
    textShadow: '0 0 20px rgba(255, 255, 255, 0.3)'
  },
  
  pageSubtitle: {
    fontSize: '18px',
    color: 'rgba(255, 255, 255, 0.8)',
    lineHeight: '1.6'
  },
  
  directoryContainer: {
    width: '100%',
    maxWidth: '800px',
    display: 'flex',
    flexDirection: 'column',
    gap: '20px',
    marginBottom: '40px'
  },
  
  directoryCard: {
    background: 'rgba(255, 255, 255, 0.05)',
    borderRadius: '16px',
    padding: '25px',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    backdropFilter: 'blur(10px)',
    display: 'flex',
    alignItems: 'flex-start',
    gap: '15px'
  },
  
  linkIcon: {
    fontSize: '24px',
    flexShrink: 0,
    marginTop: '2px'
  },
  
  directoryLink: {
    color: '#4ECDC4',
    textDecoration: 'underline',
    fontSize: '20px',
    fontWeight: '600',
    display: 'block',
    marginBottom: '10px',
    transition: 'all 0.2s ease',
    ':hover': {
      color: '#2D7D7A'
    }
  },
  
  directoryDescription: {
    color: 'rgba(255, 255, 255, 0.8)',
    fontSize: '16px',
    lineHeight: '1.6',
    marginBottom: '5px'
  },
  
  disclaimer: {
    color: 'rgba(255, 255, 255, 0.6)',
    fontSize: '14px',
    lineHeight: '1.4'
  },
  
  supportSection: {
    width: '100%',
    maxWidth: '800px',
    marginBottom: '40px'
  },
  
  supportTitle: {
    fontSize: '28px',
    fontWeight: 'bold',
    color: 'white',
    marginBottom: '25px',
    textAlign: 'center'
  },
  
  supportContainer: {
    display: 'flex',
    flexDirection: 'column',
    gap: '20px',
    marginBottom: '20px'
  },
  
  supportCard: {
    background: 'rgba(255, 255, 255, 0.05)',
    borderRadius: '16px',
    padding: '25px',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    backdropFilter: 'blur(10px)',
    display: 'flex',
    alignItems: 'flex-start',
    gap: '15px'
  },
  
  supportIcon: {
    fontSize: '24px',
    flexShrink: 0,
    marginTop: '2px'
  },
  
  supportDescription: {
    color: 'rgba(255, 255, 255, 0.8)',
    fontSize: '16px',
    lineHeight: '1.6'
  },
  
  warningBox: {
    background: 'rgba(255, 165, 0, 0.15)',
    border: '2px solid rgba(255, 165, 0, 0.4)',
    borderRadius: '16px',
    padding: '20px',
    textAlign: 'center'
  },
  
  warningText: {
    color: '#FFD700',
    fontSize: '16px',
    lineHeight: '1.6',
    margin: 0,
    fontWeight: '600'
  },
  
  sourcesSection: {
    width: '100%',
    maxWidth: '800px',
    marginBottom: '40px'
  },
  
  sourcesTitle: {
    fontSize: '28px',
    fontWeight: 'bold',
    color: 'white',
    marginBottom: '15px',
    textAlign: 'center',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '10px'
  },
  
  chartIcon: {
    fontSize: '28px'
  },
  
  sourcesIntro: {
    color: 'rgba(255, 255, 255, 0.8)',
    fontSize: '16px',
    lineHeight: '1.6',
    textAlign: 'center',
    marginBottom: '25px',
    fontStyle: 'italic'
  },
  
  statsList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '15px'
  },
  
  statItem: {
    background: 'rgba(255, 255, 255, 0.05)',
    borderRadius: '12px',
    padding: '16px 20px',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    flexWrap: 'wrap'
  },
  
  statText: {
    color: 'rgba(255, 255, 255, 0.9)',
    fontSize: '16px',
    lineHeight: '1.4'
  },
  
  statLink: {
    color: '#4ECDC4',
    textDecoration: 'underline',
    fontSize: '16px',
    fontWeight: '500',
    transition: 'all 0.2s ease',
    ':hover': {
      color: '#2D7D7A',
      textDecoration: 'none'
    }
  }
}

export default Help
