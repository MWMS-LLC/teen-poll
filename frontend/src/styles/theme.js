// src/styles/theme.js
const theme = {
  fonts: {
    // Keep your titles strong but responsive
    h1:   'clamp(24px, 6vw, 40px)',  // logo / hero
    h2:   'clamp(20px, 5vw, 36px)',  // page titles (you said 36 is fine)
    h3:   'clamp(18px, 4vw, 24px)',  // section/subtitles

    // Extras to match sizes you already use
    lead:   'clamp(16px, 3.5vw, 20px)', // for things that were 20px
    button: 'clamp(15px, 3vw, 18px)',   // for things that were ~18px

    body:  'clamp(14px, 2.5vw, 16px)',
    small: 'clamp(12px, 2vw, 14px)',
    tiny:  'clamp(11px, 1.5vw, 12px)',
  },
  colors: {
    text:   '#FFFFFF',
    accent: '#4ECDC4',
    error:  '#FF7675',
  },
  layout: { maxWidth: '800px' },
};

export default theme;
