/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        soundcloud: {
          orange: '#ff5500',
          dark:   '#111111',
          gray:   '#333333',
        },
      },
    },
  },
  plugins: [],
}
