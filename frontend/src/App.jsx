import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { AudioProvider } from './contexts/AudioContext.jsx'
import Landing from './pages/Landing.jsx'
import Category from './pages/Category.jsx'
import Block from './pages/Block.jsx'
import TooOld from './pages/TooOld.jsx'
import TooYoung from './pages/TooYoung.jsx'
import BeforeYouBegin from './pages/BeforeYouBegin.jsx'
import FAQ from './pages/FAQ.jsx'
import Help from './pages/Help.jsx'
import Privacy from './pages/Privacy.jsx'
import Contact from './pages/Contact.jsx'
import Soundtrack from './pages/Soundtrack.jsx'

function App() {
  return (
    <AudioProvider>
      <Router>
        <div className="App">
          <Routes>
            <Route path="/" element={<Landing />} />
            <Route path="/category/:categoryId" element={<Category />} />
            <Route path="/block/:blockCode" element={<Block />} />
            <Route path="/too-old" element={<TooOld />} />
            <Route path="/too-young" element={<TooYoung />} />
            <Route path="/before-you-begin" element={<BeforeYouBegin />} />
            <Route path="/faq" element={<FAQ />} />
            <Route path="/help" element={<Help />} />
            <Route path="/privacy" element={<Privacy />} />
            <Route path="/contact" element={<Contact />} />
            <Route path="/soundtrack" element={<Soundtrack />} />
          </Routes>
        </div>
      </Router>
    </AudioProvider>
  )
}

export default App
