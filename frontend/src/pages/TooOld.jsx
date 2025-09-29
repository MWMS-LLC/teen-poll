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
            This isn't just about understanding your teen. It's about reconnecting with your own voice.
          </p>
          <div style={styles.questions}>
            <p style={styles.question}>What do you wish someone had told you?</p>
            <p style={styles.question}>What do you hope your child carries forward?</p>
          </div>
          <div style={styles.comingSoon}>
            <p style={styles.comingSoonTitle}>Coming soon:</p>
            <ul style={styles.featureList}>
              <li style={styles.featureListItem}>Reflection prompts</li>
              <li style={styles.featureListItem}>Your own private answers</li>
              <li style={styles.featureListItem}><em>Bar charts showing how other parents responded, too</em></li>
            </ul>
          </div>
        </div>

        {/* For Schools Section */}
        <div style={styles.section}>
          <h2 style={styles.sectionTitle}>For Schools</h2>
          <p style={styles.sectionText}>
            Teen mental health is more visible than ever, but support is still uneven across school districts. A <a href="https://news.harvard.edu/gazette/story/2025/08/public-schools-a-weak-link-in-efforts-to-protect-teen-mental-health-study-suggests/" target="_blank" rel="noopener noreferrer" style={styles.link}>2025 Harvard Medical School study</a> found that only 30% of U.S. public schools screen students for mental health issues. Even fewer offer access to in-school mental health care or telehealth. Yet the need is clear: teens today are navigating stress, social media pressure, identity struggles, and more—and often feel alone in it.
          </p>
          <p style={styles.sectionText}>
            Surveys and screenings are important—but expensive. It's understandable that many schools can't do them frequently. Our platform is not a replacement for clinical care, but it offers a free emotional reflection tool that complements school efforts and gives students a safe way to express what they're feeling.
          </p>

          <h3 style={styles.sectionSubtitle}>The Power of Listening</h3>
          <p style={styles.sectionText}>
            Our platform was designed to be a space where teens can reflect on their feelings, make sense of tough experiences, and feel seen by others going through similar things. But making that space emotionally safe requires thoughtful input from real teens—especially on how things are worded, what tone feels safe, and what visuals feel honest.
          </p>

          <h3 style={styles.sectionSubtitle}>Student Voices Already Involved</h3>
          <p style={styles.sectionText}>
            Two female students from Seaforth High School (NC) have already helped shape our project by giving detailed feedback on the wording and emotional tone of reflection questions. Their insight helped us avoid adult-sounding phrases and ensure the platform feels teen-centered, not adult-scripted.
          </p>
          <p style={styles.sectionText}>
            Two students from Chapel Hill High School (NC) have also shared their thoughts as male teens—emphasizing how hard it is for boys to talk about emotions, and why safe spaces matter. All four students appreciated the platform's anonymous format—it gave them space to open up and helped them feel less alone with their thoughts.
          </p>

          <h3 style={styles.sectionSubtitle}>Why Monthly School Surveys Matter</h3>
          <p style={styles.sectionText}>
            One of the high schools we know currently offers frequent student mental health surveys—a standout practice. This kind of consistent listening not only signals care, but can surface needs before they turn into crises. In contrast, some districts only survey students about teachers, or conduct student check-ins once or twice a year. We hope to support the kind of listening some schools are already modeling.
          </p>

          <h3 style={styles.sectionSubtitle}>How Schools Can Help</h3>
          <p style={styles.sectionText}>
            We would love to involve a few more students from different backgrounds. Their voices can help ensure our app resonates with a wide range of users. We are simply inviting honest feedback from those who understand what it feels like to grow up today.
          </p>
          <p style={styles.sectionText}>
            If your school is interested, please reach out. We are happy to collaborate with counselors, club advisors, or teachers to involve students in a safe and meaningful way.
          </p>
          
          <div style={styles.comingSoon}>
            <p style={styles.comingSoonTitle}>Please contact us at</p>
            <p style={styles.contactEmail}>
              <a href="mailto:info@MyWorldMySay.com" style={styles.emailLink}>info@MyWorldMySay.com</a>
            </p>
          </div>

          <p style={styles.noteText}>
            Note: This page is for school administrators, counselors, educators, and parents. Teens using the app will continue to engage anonymously and safely inside the app environment.
          </p>
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
  }
}

export default TooOld
