/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Custom colors for severity levels
        severity: {
          critical: '#DC2626',
          high: '#F59E0B',
          medium: '#3B82F6',
          low: '#10B981',
          unknown: '#6B7280'
        },
        // Custom colors for agent status
        status: {
          active: '#10B981',
          inactive: '#EF4444',
          deploying: '#3B82F6',
          failed: '#DC2626'
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['Fira Code', 'monospace']
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography')
  ],
}
