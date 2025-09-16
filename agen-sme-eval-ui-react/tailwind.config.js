/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // NVIDIA-inspired color palette
        nvidia: {
          green: '#76B900',
          'green-dark': '#5A8A00',
          'green-light': '#8CC63F',
          'green-accent': '#A8D65B',
        },
        dark: {
          primary: '#0D1117',
          secondary: '#161B22',
          tertiary: '#21262D',
          accent: '#30363D',
        },
        gray: {
          50: '#F6F8FA',
          100: '#E1E4E8',
          200: '#D0D7DE',
          300: '#AFB8C1',
          400: '#8B949E',
          500: '#6E7781',
          600: '#57606A',
          700: '#424A53',
          800: '#32383F',
          900: '#24292F',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Consolas', 'monospace'],
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        glow: {
          '0%': { boxShadow: '0 0 5px #76B900' },
          '100%': { boxShadow: '0 0 20px #76B900, 0 0 30px #76B900' },
        }
      },
      backdropBlur: {
        xs: '2px',
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}
