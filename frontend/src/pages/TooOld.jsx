import React from 'react'
import Footer from '../components/Footer.jsx'

const TooOld = () => {
  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.mainTitle}>
          Welcome, Grown-Ups 👋
        </h1>
        <p style={styles.tagline}>
          Your world, your say—too.
        </p>
      </div>

      <div style={styles.content}>
        {/* For Parents Section */}
        <div style={styles.section}>
          <h2 style={styles.sectionTitle}>For Parents</h2>
          <p style={styles.sectionText}>
            Want to know how other parents feel about raising teens—just like your child does with their peers?
            All responses are anonymous, and you'll see bar charts showing different parent perspectives.
          </p>
          <p style={styles.sectionText}>
            You'll also be able to notice trends from teens themselves—what's on their minds, what challenges they face, and what gives them strength.
          </p>
          <p style={styles.sectionText}>
            This space is designed for validation, not judgment. You'll find encouragement, and sometimes gentle advice, but never pressure.
          </p>
          <p style={styles.sectionText}>
            If you'd like to get a feel for our mission, listen to the soundtrack created with teens. The songs reflect the same themes parents and teens explore here.
          </p>
          <div style={styles.parentsLinkContainer}>
            <p style={styles.parentsLinkText}>
              <strong>Ready to start reflecting now?</strong>
            </p>
            <a 
              href="https://parents.myworldmysay.com" 
              target="_blank" 
              rel="noopener noreferrer"
              style={styles.parentsLink}
            >
              Visit Parents Poll →
            </a>
          </div>
        </div>

        {/* For Schools Section */}
        <div style={styles.section}>
          <h2 style={styles.sectionTitle}>For Schools</h2>
          <p style={styles.sectionText}>
            Schools don't need to solve everything—but they can help teens listen to each other anonymously.
          </p>
          <p style={styles.sectionText}>
            Our polls validate feelings, give parents insight, and remind teens they're not alone. The empathetic, uplifting soundtrack makes the experience inviting.
          </p>
          <p style={styles.sectionText}>
            Teens say they value this app for its honesty, the anonymity, and the comfort of knowing others feel the same way.
          </p>
          <p style={styles.sectionText}>
            The more students who join—from different communities—the richer the insights become.
          </p>
          
          <div style={styles.parentsLinkContainer}>
            <a 
              href="https://schools.myworldmysay.com" 
              target="_blank" 
              rel="noopener noreferrer"
              style={styles.parentsLink}
            >
              Visit Schools Page →
            </a>
          </div>
        </div>

        {/* For Other Grown-Ups Section */}
        <div style={styles.section}>
          <h2 style={styles.sectionTitle}>For Other Grown-Ups</h2>
          <p style={styles.sectionText}>
            Whether you're a mentor, teacher, sibling, or just someone who's lived a little—you've got a story, a lens, a voice.
          </p>
          <p style={styles.sectionText}>
            We'll be asking real questions—about:
          </p>
          <div style={styles.topics}>
            <span style={styles.topic}>❤️ heartbreak</span>
            <span style={styles.topic}>👥 friendship</span>
            <span style={styles.topic}>💼 work</span>
            <span style={styles.topic}>🌱 healing</span>
            <span style={styles.topic}>🌀 choices you made (or didn't)</span>
          </div>
          <div style={styles.comingSoon}>
            <p style={styles.comingSoonTitle}>Coming soon:</p>
            <ul style={styles.featureList}>
              <li style={styles.featureListItem}>Thought-provoking polls</li>
              <li style={styles.featureListItem}>Insightful results</li>
              <li style={styles.featureListItem}>A space to reflect, laugh, regret, and grow</li>
              <li style={styles.featureListItem}>Sometimes, seeing the bar chart is all it takes to realize you're not the only one.</li>
            </ul>
          </div>
        </div>

        {/* Back Button */}
        <div style={styles.backButtonContainer}>
          <button 
            onClick={() => window.history.back()}
            style={styles.backButton}
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

const styles = {
  container: {
    minHeight: '100vh',
    background: 'linear-gradient(135deg, #0A0F2B 0%, #1A1F3B 50%, #2A2F4B 100%)',
    padding: '40px 20px',
    color: 'white'
  },
  
  header: {
    textAlign: 'center',
    marginBottom: '50px'
  },
  
  mainTitle: {
    fontSize: '48px',
    fontWeight: 'bold',
    marginBottom: '20px',
    background: 'linear-gradient(135deg, #FFD93D 0%, #FFA500 100%)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    backgroundClip: 'text'
  },
  
  tagline: {
    fontSize: '24px',
    color: 'rgba(255, 255, 255, 0.9)',
    fontStyle: 'italic'
  },
  
  content: {
    maxWidth: '800px',
    margin: '0 auto'
  },
  
  section: {
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    borderRadius: '20px',
    padding: '30px',
    marginBottom: '30px',
    border: '1px solid rgba(255, 255, 255, 0.2)',
    backdropFilter: 'blur(10px)'
  },
  
  sectionTitle: {
    fontSize: '28px',
    fontWeight: 'bold',
    marginBottom: '20px',
    color: '#4ECDC4'
  },
  
  sectionSubtitle: {
    fontSize: '22px',
    fontWeight: 'bold',
    marginTop: '30px',
    marginBottom: '15px',
    color: '#4ECDC4'
  },
  
  sectionText: {
    fontSize: '18px',
    lineHeight: '1.6',
    marginBottom: '20px',
    color: 'rgba(255, 255, 255, 0.9)'
  },
  
  questions: {
    marginBottom: '25px'
  },
  
  question: {
    fontSize: '20px',
    fontWeight: '600',
    color: '#FFD93D',
    marginBottom: '10px',
    fontStyle: 'italic'
  },
  
  topics: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '15px',
    marginBottom: '25px'
  },
  
  topic: {
    backgroundColor: 'rgba(78, 205, 196, 0.2)',
    padding: '8px 16px',
    borderRadius: '20px',
    fontSize: '16px',
    border: '1px solid rgba(78, 205, 196, 0.4)'
  },
  
  comingSoon: {
    backgroundColor: 'rgba(255, 217, 61, 0.1)',
    borderRadius: '15px',
    padding: '20px',
    border: '1px solid rgba(255, 217, 61, 0.3)'
  },
  
  comingSoonTitle: {
    fontSize: '18px',
    fontWeight: 'bold',
    color: '#FFD93D',
    marginBottom: '15px'
  },
  
  featureList: {
    listStyle: 'none',
    padding: 0,
    margin: 0
  },
  
  featureListItem: {
    fontSize: '16px',
    color: 'rgba(255, 255, 255, 0.8)',
    marginBottom: '8px',
    paddingLeft: '20px',
    position: 'relative'
  },
  
  backButtonContainer: {
    textAlign: 'center',
    marginTop: '40px'
  },
  
  backButton: {
    padding: '15px 30px',
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    color: 'white',
    border: '1px solid rgba(255, 255, 255, 0.3)',
    borderRadius: '25px',
    cursor: 'pointer',
    fontSize: '18px',
    fontWeight: '500',
    transition: 'all 0.3s ease',
    backdropFilter: 'blur(10px)'
  },
  
  link: {
    color: '#4ECDC4',
    textDecoration: 'underline',
    fontWeight: '500'
  },
  
  noteText: {
    fontSize: '16px',
    lineHeight: '1.5',
    marginTop: '25px',
    color: 'rgba(255, 255, 255, 0.7)',
    fontStyle: 'italic'
  },
  
  contactEmail: {
    fontSize: '18px',
    color: 'rgba(255, 255, 255, 0.9)',
    margin: '10px 0 0 0',
    textAlign: 'center'
  },
  
  emailLink: {
    color: '#FFD93D',
    textDecoration: 'none',
    fontWeight: '600',
    fontSize: '20px'
  },

  parentsLinkContainer: {
    backgroundColor: 'rgba(78, 205, 196, 0.1)',
    borderRadius: '15px',
    padding: '25px',
    border: '2px solid rgba(78, 205, 196, 0.3)',
    textAlign: 'center',
    marginTop: '20px'
  },

  parentsLinkText: {
    fontSize: '18px',
    color: 'rgba(255, 255, 255, 0.9)',
    marginBottom: '15px'
  },

  parentsLink: {
    display: 'inline-block',
    padding: '15px 30px',
    backgroundColor: '#4ECDC4',
    color: 'white',
    textDecoration: 'none',
    borderRadius: '25px',
    fontSize: '18px',
    fontWeight: '600',
    transition: 'all 0.3s ease',
    boxShadow: '0 4px 15px rgba(78, 205, 196, 0.3)'
  }
}

export default TooOld
