/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'hs-gold': '#ffb100',
        'hs-brown': '#3d2b1f',
        'hs-dark': '#1a1a2e',
      },
    },
  },
  plugins: [],
}
