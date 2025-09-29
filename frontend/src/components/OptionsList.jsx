import React from 'react'

const OptionsList = ({ 
  options, 
  isCheckbox, 
  selectedOptions, 
  onOptionChange, 
  onSingleChoice, 
  onOtherClick,
  onOtherSubmit,
  otherText,
  setOtherText,
  showOtherInput,
  isSubmitting,
  maxSelect
}) => {


  const handleOptionClick = (optionSelect) => {
    if (isSubmitting) return // Disable clicks while submitting
    
    if (isCheckbox) {
      // For checkboxes, toggle the selection
      const isSelected = selectedOptions.includes(optionSelect)
      
      if (!isSelected && maxSelect && selectedOptions.length >= maxSelect) {
        // Don't allow more selections if max limit reached
        return
      }
      
      onOptionChange(optionSelect, !isSelected)
    } else {
      // For single choice, submit immediately
      onSingleChoice(optionSelect)
    }
  }

  const handleOtherClick = () => {
    onOtherClick()
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
      {options.map((option, index) => {
        // Safety check for option data
        if (!option || !option.option_select || !option.option_text) {
          console.error('Invalid option data:', option)
          return (
            <div key={`invalid-${index}`} style={{ 
              padding: '10px', 
              backgroundColor: '#fff5f5', 
              border: '1px solid #ff6b6b',
              borderRadius: '4px',
              color: '#d63031',
              fontSize: '14px'
            }}>
              <strong>Error:</strong> Invalid option data
              <br />
              <small>{JSON.stringify(option)}</small>
            </div>
          )
        }

        if (option.option_select === 'OTHER') {
          return (
            <div key={option.option_select}>
              {isCheckbox ? (
                // Checkbox OTHER option
                <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
                  <input
                    type="checkbox"
                    checked={selectedOptions.includes(option.option_select)}
                    onChange={(e) => onOptionChange(option.option_select, e.target.checked)}
                    disabled={!selectedOptions.includes(option.option_select) && maxSelect && selectedOptions.length >= maxSelect}
                    style={{ 
                      transform: 'scale(1.3)',
                      accentColor: '#2D7D7A',
                      opacity: (!selectedOptions.includes(option.option_select) && maxSelect && selectedOptions.length >= maxSelect) ? 0.5 : 1
                    }}
                  />
                  <label 
                    style={{ 
                      cursor: (!selectedOptions.includes(option.option_select) && maxSelect && selectedOptions.length >= maxSelect) ? 'not-allowed' : 'pointer', 
                      flex: 1,
                      padding: '15px 20px',
                      border: '1px solid rgba(255, 255, 255, 0.2)',
                      borderRadius: '12px',
                      backgroundColor: selectedOptions.includes(option.option_select) 
                        ? 'rgba(45, 125, 122, 0.15)' 
                        : 'transparent',
                      color: selectedOptions.includes(option.option_select) 
                        ? '#2D7D7A' 
                        : (!selectedOptions.includes(option.option_select) && maxSelect && selectedOptions.length >= maxSelect) ? 'rgba(255, 255, 255, 0.5)' : 'white',
                      fontSize: '16px',
                      fontWeight: '500',
                      transition: 'all 0.2s ease',
                      borderColor: selectedOptions.includes(option.option_select) 
                        ? '#2D7D7A' 
                        : 'rgba(255, 255, 255, 0.2)'
                    }}
                    onClick={() => {
                      if (!(!selectedOptions.includes(option.option_select) && maxSelect && selectedOptions.length >= maxSelect)) {
                        onOptionChange(option.option_select, !selectedOptions.includes(option.option_select))
                      }
                    }}
                  >
                    {option.option_text}
                  </label>
                </div>
              ) : (
                // Single choice OTHER option - show as clickable button
                <button
                  style={{ 
                    cursor: 'pointer', 
                    width: '100%',
                    padding: '18px 24px',
                    border: '1px solid rgba(255, 255, 255, 0.2)',
                    borderRadius: '16px',
                    backgroundColor: 'transparent',
                    color: 'white',
                    fontSize: '16px',
                    fontWeight: '500',
                    textAlign: 'left',
                    transition: 'all 0.2s ease',
                    boxShadow: 'none',
                    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Helvetica Neue", Helvetica, Arial, sans-serif',
                    lineHeight: '1.5'
                  }}
                  onClick={handleOtherClick}
                  className="option-button-hover"
                >
                  {option.option_text}
                </button>
              )}
              
              {/* Show text input when OTHER is selected */}
              {(isCheckbox && selectedOptions.includes(option.option_select)) || 
               (!isCheckbox && showOtherInput) ? (
                <div style={{ marginTop: '10px', marginLeft: '30px' }}>
                  <textarea
                    value={otherText || ''}
                    onChange={(e) => setOtherText(e.target.value)}
                    placeholder="We may not see this in time, so please don't use it for anything urgent."
                    style={{
                      width: '100%',
                      minHeight: '80px',
                      padding: '8px',
                      border: '1px solid #ddd',
                      borderRadius: '4px',
                      fontSize: '14px'
                    }}
                  />
                  {!isCheckbox && (
                    <button
                      onClick={() => {
                        if (otherText.trim()) {
                          // Submit OTHER response for radio questions
                          onOtherSubmit()
                        }
                      }}
                      style={{
                        marginTop: '10px',
                        padding: '8px 16px',
                        backgroundColor: '#007bff',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer'
                      }}
                    >
                      Submit
                    </button>
                  )}
                </div>
              ) : null}
            </div>
          )
        }

        return (
          <div key={option.option_select}>
            {isCheckbox ? (
              // Checkbox question - show checkbox with label
              <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
                <input
                  type="checkbox"
                  checked={selectedOptions.includes(option.option_select)}
                  onChange={(e) => onOptionChange(option.option_select, e.target.checked)}
                  disabled={!selectedOptions.includes(option.option_select) && maxSelect && selectedOptions.length >= maxSelect}
                  style={{ 
                    transform: 'scale(1.3)',
                    accentColor: '#2D7D7A',
                    opacity: (!selectedOptions.includes(option.option_select) && maxSelect && selectedOptions.length >= maxSelect) ? 0.5 : 1
                  }}
                />
                                  <label 
                    style={{ 
                      cursor: (!selectedOptions.includes(option.option_select) && maxSelect && selectedOptions.length >= maxSelect) ? 'not-allowed' : 'pointer', 
                      flex: 1,
                      padding: '15px 20px',
                      border: '1px solid rgba(255, 255, 255, 0.2)',
                      borderRadius: '12px',
                      backgroundColor: selectedOptions.includes(option.option_select) 
                        ? 'rgba(45, 125, 122, 0.15)' 
                        : 'transparent',
                      color: selectedOptions.includes(option.option_select) 
                        ? '#2D7D7A' 
                        : (!selectedOptions.includes(option.option_select) && maxSelect && selectedOptions.length >= maxSelect) ? 'rgba(255, 255, 255, 0.5)' : 'white',
                      fontSize: '16px',
                      fontWeight: '500',
                      transition: 'all 0.2s ease',
                      borderColor: selectedOptions.includes(option.option_select) 
                        ? '#2D7D7A' 
                        : 'rgba(255, 255, 255, 0.2)'
                    }}
                  onClick={() => {
                    if (!(!selectedOptions.includes(option.option_select) && maxSelect && selectedOptions.length >= maxSelect)) {
                      onOptionChange(option.option_select, !selectedOptions.includes(option.option_select))
                    }
                  }}
                >
                  {option.option_text}
                </label>
              </div>
            ) : (
              // Single choice question - show as clickable button (no radio)
              <button
                disabled={isSubmitting}
                style={{ 
                  cursor: isSubmitting ? 'not-allowed' : 'pointer', 
                  width: '100%',
                  padding: '18px 24px',
                  border: '1px solid rgba(255, 255, 255, 0.2)',
                  borderRadius: '16px',
                  backgroundColor: isSubmitting ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
                  color: isSubmitting ? 'rgba(255, 255, 255, 0.6)' : 'white',
                  fontSize: '16px',
                  fontWeight: '500',
                  textAlign: 'left',
                  transition: 'all 0.2s ease',
                  boxShadow: 'none',
                  opacity: isSubmitting ? 0.7 : 1
                }}
                onClick={() => handleOptionClick(option.option_select)}
                className="option-button-hover"
                              >
                  {isSubmitting ? 'Submitting...' : option.option_text}
                </button>
            )}
          </div>
        )
      })}
    </div>
  )
}

export default OptionsList
