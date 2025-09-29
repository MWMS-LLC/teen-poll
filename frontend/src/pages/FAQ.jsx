import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import HamburgerMenu from '../components/HamburgerMenu.jsx'
import Footer from '../components/Footer.jsx'

const FAQ = () => {
  const navigate = useNavigate()

  const [openFaq, setOpenFaq] = useState(null)

  const faqData = [
    {
      question: "What is My World My Say?",
      answer: "My World My Say is a platform where teens can explore questions about life, emotions, and identity through anonymous polls. It's a space to hear how others feel and add your voice to the conversation."
    },
    {
      question: "Is this really anonymous?",
      answer: "Yes, completely. We don't collect your name, email, or any personal information. Your responses are linked only to a random ID that helps us group responses without knowing who you are."
    },
    {
      question: "How do the polls work?",
      answer: "Choose a category that interests you, pick a block of questions, and answer honestly. You'll see how others feel too, and get personalized insights and advice based on your responses."
    },
    {
      question: "What kind of questions are there?",
      answer: "We cover topics like friendships, relationships, school, family, emotions, and identity. The questions are designed to help teens explore their thoughts and feelings in a safe, supportive environment."
    },
    {
      question: "Who can use this app?",
      answer: "Teens aged 13-19 can use My World My Say. We've designed it specifically for the teen experience and the unique challenges and questions that come with this time in life."
    },
    {
      question: "How do you protect my privacy?",
      answer: "We use industry-standard security measures to protect your data. We never ask for personal information, and all responses are stored anonymously. Your privacy and safety are our top priorities."
    },
    {
      question: "Can I change my answers?",
      answer: "Currently, answers are final once submitted. This helps maintain the integrity of the data and ensures everyone gets honest insights from the community."
    },
    {
      question: "What if I see something concerning?",
      answer: "If you encounter content that makes you uncomfortable or concerned, please use the contact form. We're here to help and want everyone to feel safe using the platform."
    }
  ]

  const toggleFaq = (index) => {
    setOpenFaq(openFaq === index ? null : index)
  }

  return (
    <div style={styles.container}>
      {/* Hamburger Menu */}
      <HamburgerMenu />
      
      {/* Header Section */}
      <div style={styles.headerSection}>
        <div style={styles.backButton} onClick={() => navigate('/')}>
          ← Back to Home
        </div>
        <h1 style={styles.pageTitle}>FAQ & About</h1>
        <div style={styles.pageSubtitle}>
          Everything you need to know about My World My Say
        </div>
      </div>

      {/* FAQ Section */}
      <div style={styles.faqContainer}>
        {faqData.map((faq, index) => (
          <div 
            key={index} 
            style={styles.faqItem}
            className="faq-item"
          >
            <button
              style={styles.faqQuestion}
              onClick={() => toggleFaq(index)}
            >
              <span>{faq.question}</span>
              <span style={styles.faqIcon}>
                {openFaq === index ? '−' : '+'}
              </span>
            </button>
            {openFaq === index && (
              <div style={styles.faqAnswer}>
                {faq.answer}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* About Section */}
      <div style={styles.aboutSection}>
        <h2 style={styles.aboutTitle}>About My World My Say</h2>
        <p style={styles.aboutText}>
          This app grew out of real conversations—between parents, psychologists, and teens themselves. The thoughts are true. The emotions are shared.
        </p>
        <p style={styles.aboutText}>
          Most surveys ask teens what they think, but never show them the results. <strong>My World My Say</strong> changes that—giving teens a voice <em>and</em> the big picture.
        </p>
        <p style={styles.aboutText}>
          And the songs? They don't just echo pain. They lift it, shape it, and give it direction. Because we're not here to just feel—we're here to build.
        </p>
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
  
  faqContainer: {
    width: '100%',
    maxWidth: '800px',
    marginBottom: '40px'
  },
  
  faqItem: {
    background: 'rgba(255, 255, 255, 0.05)',
    borderRadius: '16px',
    marginBottom: '15px',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    backdropFilter: 'blur(10px)',
    overflow: 'hidden'
  },
  
  faqQuestion: {
    width: '100%',
    padding: '20px',
    background: 'transparent',
    border: 'none',
    color: 'white',
    fontSize: '16px',
    fontWeight: '500',
    cursor: 'pointer',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    transition: 'all 0.2s ease',
    textAlign: 'left'
  },
  
  faqIcon: {
    fontSize: '20px',
    fontWeight: 'bold',
    color: '#4ECDC4'
  },
  
  faqAnswer: {
    padding: '0 20px 20px 20px',
    color: 'rgba(255, 255, 255, 0.8)',
    fontSize: '16px',
    lineHeight: '1.6',
    borderTop: '1px solid rgba(255, 255, 255, 0.1)',
    paddingTop: '20px'
  },
  
  aboutSection: {
    width: '100%',
    maxWidth: '800px',
    background: 'rgba(255, 255, 255, 0.05)',
    borderRadius: '20px',
    padding: '30px',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    backdropFilter: 'blur(10px)',
    textAlign: 'center'
  },
  
  aboutTitle: {
    fontSize: '28px',
    fontWeight: 'bold',
    color: 'white',
    marginBottom: '25px',
    textShadow: '0 2px 4px rgba(0, 0, 0, 0.3)'
  },
  
  aboutText: {
    fontSize: '18px',
    color: 'rgba(255, 255, 255, 0.9)',
    lineHeight: '1.6',
    marginBottom: '20px'
  }
}

export default FAQ
