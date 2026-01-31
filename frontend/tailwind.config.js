/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'sage': {
          50: '#f7f9f7',
          100: '#e8f0e8',
          200: '#c9ddc9',
          300: '#a8caa8',
          400: '#87b787',
          500: '#6fa46f',
          600: '#588858',
          700: '#446b44',
          800: '#2f4e2f',
          900: '#1a311a',
        },
      },
    },
  },
  plugins: [],
}
