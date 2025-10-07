import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { fetchCategories } from '../services/apiService'
import HamburgerMenu from '../components/HamburgerMenu'
import Footer from '../components/Footer.jsx'

const Summary = () => {
  const [categoryName, setCategoryName] = useState('')
  const [loading, setLoading] = useState(true)
  const [copySuccess, setCopySuccess] = useState(false)
  const { categoryId } = useParams()
  const navigate = useNavigate()

  useEffect(() => {
    const loadCategoryName = async () => {
      try {
        const categories = await fetchCategories()
        const category = categories.find(cat => cat.id === parseInt(categoryId))
        if (category) {
          setCategoryName(category.category_name.replace(/_/g, ' '))
        }
      } catch (err) {
        console.error('Error loading category:', err)
      } finally {
        setLoading(false)
      }
    }
    loadCategoryName()
  }, [categoryId])

  const getSummaryContent = () => {
    const summaries = {
      '1st Thing 1st': {
        validation: "You've shared what you're grateful for and the affirmations that matter to you. Every moment of gratitude you notice, no matter how small, shifts something inside. You're building a practice that grounds you.",
        advice: "Keep checking in with yourself like this. Notice what feels good, what lifts you up, what you'd want more of. Gratitude isn't about forcing positivity—it's about seeing what's real and what's yours.",
        future: "Five years from now, this habit of noticing the good will be your anchor. When life gets heavy, you'll know how to find light. The gratitude you practice today becomes the resilience you carry tomorrow."
      },
      'Love': {
        validation: "You've explored how love shows up in your life right now—the crushes, the questions, the feelings that are confusing and exciting all at once. Whatever you're feeling, it's real and it's yours.",
        advice: "Trust your gut. If something feels off, it probably is. If something feels right, take your time. You're learning what you want, what you deserve, and what love should feel like—and that takes time.",
        future: "Five years from now, the boundaries you're learning now will protect your heart. The self-respect you're building today will guide every relationship you choose. You're figuring out love—and that's powerful."
      },
      'Friends': {
        validation: "You've shared thoughts about your friendships—who lifts you up, who drains you, and how you show up for the people you care about. Friendships shape so much of who you're becoming.",
        advice: "Keep choosing friends who see you, support you, and let you be yourself. It's okay to outgrow people. It's okay to set boundaries. Real friends grow with you, not away from you.",
        future: "Five years from now, you'll look back and realize which friendships were meant to last and which were just for a season. The loyalty and trust you're building now becomes the foundation of every connection you make."
      },
      'Online Life': {
        validation: "You've navigated questions about social media, internet culture, and the strange balance between online and real life. It's a lot to manage, and you're doing it in real time.",
        advice: "Remember: what you see online isn't the whole story. Comparison is a trap. Your worth isn't measured in likes or followers. Use the internet as a tool, not a mirror.",
        future: "Five years from now, the self-awareness you're building now will help you stay grounded in a hyperconnected world. You'll know when to log off, when to speak up, and when to just live offline."
      },
      'Pinky': {
        validation: "You've shared what makes you feel pretty, powerful, or like yourself. Those little things—a song, a look, a moment—matter more than you think. They're how you claim space in the world.",
        advice: "Keep finding those moments. Notice what makes you feel good in your own skin. Confidence isn't about being perfect—it's about knowing your own vibe and owning it.",
        future: "Five years from now, the self-love you're building today will carry you through every room you walk into. The power you feel now becomes the presence you bring later."
      },
      'Lowkey': {
        validation: "You've explored how you recharge, what you do when you need space, and how you take care of yourself when the world gets loud. That self-awareness is a strength.",
        advice: "Keep protecting your peace. It's okay to step back. It's okay to say no. Taking time for yourself isn't selfish—it's survival.",
        future: "Five years from now, the boundaries you're setting now will protect your energy and your mental health. You'll know when to give and when to retreat—and that balance will save you."
      },
      'Personal': {
        validation: "You've shared thoughts about who you are, what you've learned about yourself, and what makes you... you. Identity is a journey, not a destination, and you're figuring it out.",
        advice: "Keep asking yourself who you want to be. Keep trying new things. You're allowed to change, grow, and rewrite your own story as you go.",
        future: "Five years from now, you'll look back on this time and see how much you've grown. The curiosity and courage you're showing now becomes the confidence you'll carry forward."
      },
      'Healing': {
        validation: "You've shared what helps you heal, how you process hurt, and what growth looks like for you. Healing isn't linear, and you're navigating it with courage.",
        advice: "Keep being kind to yourself. Healing takes time, and it's okay if some days are harder than others. You're not broken—you're becoming.",
        future: "Five years from now, the healing work you're doing today will show up as strength, empathy, and resilience. You'll know how to sit with pain and still choose hope."
      },
      'Defense': {
        validation: "You've explored how you protect yourself, how you respond to bullies or negativity, and what makes you feel strong. Building emotional armor is smart, but so is knowing when to let it down.",
        advice: "Stand up for yourself, but don't harden completely. You can be strong and soft at the same time. Protect your peace, but don't close yourself off from connection.",
        future: "Five years from now, the strength you're building now will help you face challenges with confidence. You'll know when to fight and when to walk away—and that wisdom will serve you forever."
      },
      'Family': {
        validation: "You've shared thoughts about your family—what's good, what's hard, and how you navigate home life. Family relationships are complex, and you're doing your best.",
        advice: "Keep communicating, even when it's tough. Set boundaries when you need to. Remember: you can love your family and still need space to be yourself.",
        future: "Five years from now, you'll have more clarity about your family dynamics and your role in them. The communication skills and emotional awareness you're building now will shape every relationship you have."
      },
      'Future': {
        validation: "You've shared your dreams, your fears about the future, and what you hope your life will look like. Thinking about the future can be exciting and overwhelming—but you're doing it.",
        advice: "Keep dreaming, but stay present too. The future you want starts with the choices you make today. Build skills, stay curious, and trust that you're figuring it out.",
        future: "Five years from now, you'll see how the vision you're holding today starts to take shape. The dreams you plant now become the goals you chase later—and you've got this."
      },
      'School': {
        validation: "You've explored how school feels for you—what's working, what's hard, and how you're navigating it all. School isn't just about grades; it's about figuring out who you are in that space.",
        advice: "Do your best, but don't tie your worth to your grades. Learn what interests you, build skills that matter, and remember: there are many paths to success.",
        future: "Five years from now, you'll look back and realize that what you learned about yourself in school mattered more than the tests. The resilience and curiosity you're building now will carry you through college, work, and life."
      },
      'Fun Stuff': {
        validation: "You've shared what brings you joy—games, music, sports, food, and all the little things that make life feel good. Joy matters. Fun matters. You're allowed to enjoy yourself.",
        advice: "Keep making space for what you love. Life gets busy, but joy is what keeps you alive. Don't lose the things that make you feel like yourself.",
        future: "Five years from now, you'll be grateful you stayed connected to what makes you happy. The hobbies and passions you nurture now become the outlets that keep you grounded later."
      },
      'Chaos': {
        validation: "You've shared the awkward, messy, hilarious moments that make life unpredictable. Those moments are real, relatable, and honestly? They're what make the best stories.",
        advice: "Laugh at yourself. Embrace the chaos. Life is messy for everyone—you're just honest enough to admit it.",
        future: "Five years from now, you'll look back on these chaotic moments and realize they were part of what made you resilient, funny, and real. The humor you carry now becomes the lightness you bring to hard times later."
      }
    }

    return summaries[categoryName] || {
      validation: "You've completed this category and shared your thoughts. Every response reflects your unique perspective and experience.",
      advice: "Keep engaging with these important topics. Your awareness and thoughtfulness matter.",
      future: "Five years from now, the reflection you're doing today will shape how you approach these areas of life. Every conversation and choice builds the foundation for tomorrow."
    }
  }

  const handleShare = () => {
    const shareText = `I just shared my thoughts on ${categoryName} at My World My Say!\n\nSee what teens are saying: https://myworldmysay.com`
    
    navigator.clipboard.writeText(shareText).then(() => {
      setCopySuccess(true)
      setTimeout(() => setCopySuccess(false), 3000)
    }).catch(err => {
      console.error('Failed to copy:', err)
      alert('Failed to copy link. Please try again.')
    })
  }

  if (loading) {
    return (
      <div style={styles.loadingContainer}>
        <div style={styles.loadingText}>Loading summary...</div>
        <div style={styles.loadingSpinner}></div>
      </div>
    )
  }

  const summary = getSummaryContent()

  return (
    <div style={styles.container}>
      <HamburgerMenu />

      <div style={styles.contentWrapper}>
        <div style={styles.headerSection}>
          <div style={styles.sparkleIcon}>✨</div>
          <h1 style={styles.pageTitle}>Your {categoryName} Summary</h1>
          <p style={styles.subtitle}>A reflection on your responses</p>
        </div>

        <div style={styles.summaryCard}>
          <div style={styles.section}>
            <h3 style={styles.sectionTitle}>Validation</h3>
            <p style={styles.sectionText}>{summary.validation}</p>
          </div>

          <div style={styles.divider}></div>

          <div style={styles.section}>
            <h3 style={styles.sectionTitle}>Advice</h3>
            <p style={styles.sectionText}>{summary.advice}</p>
          </div>

          <div style={styles.divider}></div>

          <div style={styles.section}>
            <h3 style={styles.sectionTitle}>Five Years Later</h3>
            <p style={styles.sectionText}>{summary.future}</p>
          </div>
        </div>

        {/* Music Suggestion */}
        <div style={styles.musicNote}>
          <span style={styles.musicNoteIcon}>🎵</span>
          <span style={styles.musicNoteText}>
            Soundtrack for this moment: 
            <button 
              style={styles.musicLink}
              onClick={() => navigate('/soundtrack?playlist=5 Years Later')}
            >
              5 Years Later
            </button>
          </span>
        </div>

        <div style={styles.futureNote}>
          <span style={styles.futureNoteIcon}>✨</span>
          <span style={styles.futureNoteText}>Personalized AI summaries coming soon!</span>
        </div>

        <div style={styles.buttonsContainer}>
          <button
            style={styles.shareButton}
            onClick={handleShare}
          >
            {copySuccess ? '✓ Copied!' : '📋 Share Link'}
          </button>

          <button
            style={styles.backButton}
            onClick={() => navigate('/')}
          >
            ← Back to Categories
          </button>
        </div>
      </div>

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

  loadingContainer: {
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    background: 'linear-gradient(135deg, #0A0F2B 0%, #1A1F3B 100%)',
    gap: '20px'
  },

  loadingText: {
    color: 'rgba(255, 255, 255, 0.8)',
    fontSize: '16px',
    fontWeight: '500'
  },

  loadingSpinner: {
    width: '40px',
    height: '40px',
    border: '4px solid rgba(255, 255, 255, 0.3)',
    borderTop: '4px solid #FFD700',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite'
  },

  contentWrapper: {
    width: '100%',
    maxWidth: '800px',
    marginTop: '40px',
    marginBottom: '40px'
  },

  headerSection: {
    textAlign: 'center',
    marginBottom: '40px'
  },

  sparkleIcon: {
    fontSize: '48px',
    marginBottom: '20px',
    animation: 'sparkle 2s ease-in-out infinite'
  },

  pageTitle: {
    fontSize: '36px',
    fontWeight: 'bold',
    color: 'white',
    marginBottom: '10px',
    textShadow: '0 0 20px rgba(255, 215, 0, 0.3)'
  },

  subtitle: {
    fontSize: '18px',
    color: 'rgba(255, 255, 255, 0.7)',
    fontStyle: 'italic'
  },

  summaryCard: {
    background: 'linear-gradient(135deg, rgba(255, 215, 0, 0.15) 0%, rgba(255, 165, 0, 0.1) 100%)',
    borderRadius: '20px',
    padding: '40px',
    border: '2px solid rgba(255, 215, 0, 0.3)',
    boxShadow: '0 10px 40px rgba(255, 215, 0, 0.2)',
    backdropFilter: 'blur(10px)',
    marginBottom: '30px'
  },

  section: {
    marginBottom: '30px'
  },

  sectionTitle: {
    fontSize: '22px',
    fontWeight: '700',
    color: '#FFD700',
    marginBottom: '15px',
    textShadow: '0 0 10px rgba(255, 215, 0, 0.5)'
  },

  sectionText: {
    fontSize: '16px',
    lineHeight: '1.8',
    color: 'rgba(255, 255, 255, 0.9)',
    whiteSpace: 'pre-line'
  },

  divider: {
    height: '1px',
    background: 'linear-gradient(90deg, transparent, rgba(255, 215, 0, 0.3), transparent)',
    marginBottom: '30px'
  },

  musicNote: {
    textAlign: 'center',
    padding: '15px',
    background: 'rgba(78, 205, 196, 0.1)',
    borderRadius: '15px',
    border: '1px solid rgba(78, 205, 196, 0.3)',
    marginBottom: '20px'
  },

  musicNoteIcon: {
    fontSize: '20px',
    marginRight: '10px'
  },

  musicNoteText: {
    fontSize: '16px',
    color: 'rgba(255, 255, 255, 0.9)',
    fontWeight: '500'
  },

  musicLink: {
    background: 'none',
    border: 'none',
    color: '#4ECDC4',
    fontSize: '16px',
    fontWeight: '600',
    cursor: 'pointer',
    textDecoration: 'underline',
    marginLeft: '5px',
    padding: '0',
    transition: 'all 0.2s ease'
  },

  futureNote: {
    textAlign: 'center',
    padding: '15px',
    background: 'rgba(255, 215, 0, 0.1)',
    borderRadius: '15px',
    border: '1px solid rgba(255, 215, 0, 0.2)',
    marginBottom: '30px'
  },

  futureNoteIcon: {
    fontSize: '20px',
    marginRight: '10px'
  },

  futureNoteText: {
    fontSize: '16px',
    color: '#FFD700',
    fontWeight: '600',
    fontStyle: 'italic'
  },

  buttonsContainer: {
    display: 'flex',
    flexDirection: 'column',
    gap: '15px',
    alignItems: 'center'
  },

  shareButton: {
    padding: '15px 40px',
    fontSize: '16px',
    fontWeight: '600',
    color: '#0A0F2B',
    background: 'linear-gradient(135deg, #FFD700 0%, #FFA500 100%)',
    border: '2px solid rgba(255, 215, 0, 0.5)',
    borderRadius: '30px',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    boxShadow: '0 8px 25px rgba(255, 215, 0, 0.4)',
    minWidth: '250px'
  },

  backButton: {
    padding: '12px 30px',
    fontSize: '16px',
    fontWeight: '600',
    color: 'rgba(255, 255, 255, 0.9)',
    background: 'rgba(255, 255, 255, 0.1)',
    border: '2px solid rgba(255, 255, 255, 0.3)',
    borderRadius: '25px',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    minWidth: '250px'
  }
}

export default Summary

