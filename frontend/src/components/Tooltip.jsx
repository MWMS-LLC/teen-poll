import React, { useState } from 'react'

const Tooltip = ({ content, children, position = 'top' }) => {
  const [isVisible, setIsVisible] = useState(false)

  // Debug logging
  console.log('Tooltip render:', { content, position, isVisible })

  const handleMouseEnter = (e) => {
    e.preventDefault()
    e.stopPropagation()
    console.log('Mouse enter, content:', content)
    setIsVisible(true)
  }
  const handleMouseLeave = (e) => {
    e.preventDefault()
    e.stopPropagation()
    console.log('Mouse leave')
    setIsVisible(false)
  }
  const handleTouchStart = () => setIsVisible(true)
  const handleTouchEnd = () => {
    // Delay hiding on mobile to allow reading
    setTimeout(() => setIsVisible(false), 2000)
  }

  const getPositionStyles = () => {
    switch (position) {
      case 'top':
        return {
          bottom: '100%',
          left: '50%',
          transform: 'translateX(-50%)',
          marginBottom: '8px'
        }
      case 'bottom':
        return {
          top: '100%',
          left: '50%',
          transform: 'translateX(-50%)',
          marginTop: '8px'
        }
      case 'left':
        return {
          right: '100%',
          top: '50%',
          transform: 'translateY(-50%)',
          marginRight: '8px'
        }
      case 'right':
        return {
          left: '100%',
          top: '50%',
          transform: 'translateY(-50%)',
          marginLeft: '8px'
        }
      default:
        return {
          bottom: '100%',
          left: '50%',
          transform: 'translateX(-50%)',
          marginBottom: '8px'
        }
    }
  }

  return (
    <div 
      style={{ position: 'relative', display: 'inline-block' }}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onTouchStart={handleTouchStart}
      onTouchEnd={handleTouchEnd}
    >
      <div 
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        style={{ display: 'inline-block' }}
      >
        {children}
      </div>
      
      {isVisible && content && (
        <div
          style={{
            position: 'absolute',
            zIndex: 9999,
            backgroundColor: 'rgba(45, 125, 122, 0.95)',
            color: 'white',
            padding: '12px 16px',
            borderRadius: '12px',
            fontSize: '14px',
            lineHeight: '1.4',
            width: '240px',
            whiteSpace: 'pre-wrap',
            textAlign: 'center',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)',
            backdropFilter: 'blur(12px)',
            border: '2px solid rgba(255, 255, 255, 0.3)',
            userSelect: 'none',
            WebkitUserSelect: 'none',
            MozUserSelect: 'none',
            msUserSelect: 'none',
            ...getPositionStyles()
          }}
        >
          {content}
          
          {/* Tooltip arrow */}
          <div
            style={{
              position: 'absolute',
              width: '0',
              height: '0',
              ...(position === 'top' && {
                top: '100%',
                left: '50%',
                transform: 'translateX(-50%)',
                borderLeft: '6px solid transparent',
                borderRight: '6px solid transparent',
                borderTop: '6px solid rgba(26, 31, 59, 0.95)'
              }),
              ...(position === 'bottom' && {
                bottom: '100%',
                left: '50%',
                transform: 'translateX(-50%)',
                borderLeft: '6px solid transparent',
                borderRight: '6px solid transparent',
                borderBottom: '6px solid rgba(26, 31, 59, 0.95)'
              }),
              ...(position === 'left' && {
                left: '100%',
                top: '50%',
                transform: 'translateY(-50%)',
                borderTop: '6px solid transparent',
                borderBottom: '6px solid transparent',
                borderLeft: '6px solid rgba(26, 31, 59, 0.95)'
              }),
              ...(position === 'right' && {
                right: '100%',
                top: '50%',
                transform: 'translateY(-50%)',
                borderTop: '6px solid transparent',
                borderBottom: '6px solid transparent',
                borderRight: '6px solid rgba(26, 31, 59, 0.95)'
              })
            }}
          />
        </div>
      )}
    </div>
  )
}

export default Tooltip
