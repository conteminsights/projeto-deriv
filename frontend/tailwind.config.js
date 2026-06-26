/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Dark theme baseado no ZeeK original
        zeek: {
          'bg': '#09091f',
          'bg-secondary': '#11182d',
          'bg-tertiary': '#1a2340',
          'border': '#202832',
          'border-light': '#394554',
          'text': '#e0e6f0',
          'text-secondary': '#8892a8',
          'text-muted': '#5a6478',
          'accent': '#f86525',
          'accent-light': '#ff8a50',
          'accent-dark': '#e05515',
          'accent-gold': '#ffd64f',
          'profit': '#00ff44',
          'loss': '#ff4444',
          'warning': '#ffaa00',
          'call': '#00c853',
          'put': '#ff1744',
        },
      },
      fontFamily: {
        sans: ['Inter', 'Segoe UI', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
    },
  },
  plugins: [],
}
