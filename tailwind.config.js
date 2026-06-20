/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        navy: {
          950: '#040810',
          900: '#081120',
          800: '#0B1220',
          700: '#0d1630',
          600: '#111e3a',
          500: '#162244',
        },
        electric: {
          DEFAULT: '#00D4FF',
          dim: '#0099cc',
          glow: 'rgba(0, 212, 255, 0.3)',
        },
        plasma: {
          DEFAULT: '#0066FF',
          dim: '#0044cc',
        },
        threat: {
          critical: '#FF1744',
          high: '#FF6D00',
          medium: '#FFD600',
          low: '#00E676',
          normal: '#00BFA5',
        },
        panel: 'rgba(8, 17, 32, 0.85)',
      },
      fontFamily: {
        orbitron: ['Orbitron', 'monospace'],
        inter: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      animation: {
        'pulse-ring': 'pulseRing 2s ease-out infinite',
        'pulse-ring-fast': 'pulseRing 1s ease-out infinite',
        'scan': 'scan 3s linear infinite',
        'flicker': 'flicker 4s ease-in-out infinite',
        'blink': 'blink 1.2s step-start infinite',
        'glow-pulse': 'glowPulse 2s ease-in-out infinite',
        'slide-in-left': 'slideInLeft 0.4s ease-out',
        'slide-in-right': 'slideInRight 0.4s ease-out',
        'fade-in': 'fadeIn 0.5s ease-out',
        'data-stream': 'dataStream 20s linear infinite',
      },
      keyframes: {
        pulseRing: {
          '0%': { transform: 'scale(0.95)', opacity: '1' },
          '100%': { transform: 'scale(2.5)', opacity: '0' },
        },
        scan: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100vh)' },
        },
        flicker: {
          '0%, 100%': { opacity: '1' },
          '92%': { opacity: '1' },
          '93%': { opacity: '0.8' },
          '94%': { opacity: '1' },
          '96%': { opacity: '0.9' },
          '97%': { opacity: '1' },
        },
        blink: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0' },
        },
        glowPulse: {
          '0%, 100%': { boxShadow: '0 0 10px rgba(0, 212, 255, 0.4)' },
          '50%': { boxShadow: '0 0 25px rgba(0, 212, 255, 0.8), 0 0 50px rgba(0, 212, 255, 0.3)' },
        },
        slideInLeft: {
          '0%': { transform: 'translateX(-20px)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        slideInRight: {
          '0%': { transform: 'translateX(20px)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        dataStream: {
          '0%': { transform: 'translateY(0)' },
          '100%': { transform: 'translateY(-50%)' },
        },
      },
      backdropBlur: {
        xs: '2px',
      },
      boxShadow: {
        'glow-blue': '0 0 20px rgba(0, 212, 255, 0.4), 0 0 60px rgba(0, 212, 255, 0.1)',
        'glow-red': '0 0 20px rgba(255, 23, 68, 0.5), 0 0 60px rgba(255, 23, 68, 0.2)',
        'glow-green': '0 0 15px rgba(0, 230, 118, 0.4)',
        'glow-orange': '0 0 15px rgba(255, 109, 0, 0.4)',
        'panel': '0 8px 32px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255,255,255,0.05)',
        'card': '0 4px 24px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(0, 212, 255, 0.05)',
      },
    },
  },
  plugins: [],
}
