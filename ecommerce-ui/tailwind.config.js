// ESM
import forms from '@tailwindcss/forms'

/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: { brand: { 50: '#f2f8ff', 600: '#2563eb', 700: '#1d4ed8' } },
    },
  },
  plugins: [forms],
}
