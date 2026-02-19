/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Space Grotesk"', 'sans-serif'],
      },
      colors: {
        felixo: {
          purple: '#C084FC',
          'purple-bright': '#A855F7',
        },
        soundcloud: {
          orange: '#ff5500',
          dark:   '#111111',
          gray:   '#333333',
        },
      },
      keyframes: {
        'card-glow-breathe': {
          '0%, 100%': {
            boxShadow: '0 0 0 1px rgba(192,132,252,0.2), 0 0 28px rgba(168,85,247,0.12)',
          },
          '50%': {
            boxShadow: '0 0 0 1px rgba(192,132,252,0.32), 0 0 44px rgba(168,85,247,0.26)',
          },
        },
        'title-glow-purple': {
          '0%, 100%': { textShadow: '0 0 12px rgba(192,132,252,0.35)' },
          '50%': { textShadow: '0 0 22px rgba(168,85,247,0.8)' },
        },
        'gradient-orbit': {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },
        'text-glow-breathe': {
          '0%, 100%': { textShadow: '0 0 6px rgba(255,255,255,0.18)' },
          '50%': { textShadow: '0 0 12px rgba(255,255,255,0.35)' },
        },
      },
      animation: {
        'card-glow-breathe': 'card-glow-breathe 3s ease-in-out infinite',
        'title-glow-purple': 'title-glow-purple 3s ease-in-out infinite',
        'gradient-orbit': 'gradient-orbit 7.5s linear infinite',
        'text-glow-breathe': 'text-glow-breathe 3.8s ease-in-out infinite',
      },
    },
  },
  plugins: [],
}
