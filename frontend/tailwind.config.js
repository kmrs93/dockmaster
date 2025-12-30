/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'dm-dark': '#0f172a',
        'dm-card': '#1e293b',
        'dm-accent': '#3b82f6'
      }
    },
  },
  plugins: [],
}
