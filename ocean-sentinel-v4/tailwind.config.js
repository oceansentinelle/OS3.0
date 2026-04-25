/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
    './index.html',
  ],
  prefix: "",
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      // Mobile-First Typography Scale (Optimisé pour ostréiculteurs en extérieur)
      fontSize: {
        'xs': ['14px', { lineHeight: '1.5', letterSpacing: '0.01em' }],
        'sm': ['16px', { lineHeight: '1.5', letterSpacing: '0.01em' }],
        'base': ['18px', { lineHeight: '1.6', letterSpacing: '0.005em' }],
        'lg': ['20px', { lineHeight: '1.6', letterSpacing: '0.005em' }],
        'xl': ['24px', { lineHeight: '1.5', letterSpacing: '0em' }],
        '2xl': ['28px', { lineHeight: '1.4', letterSpacing: '-0.01em' }],
        '3xl': ['36px', { lineHeight: '1.3', letterSpacing: '-0.015em' }],
        '4xl': ['42px', { lineHeight: '1.2', letterSpacing: '-0.02em' }],
        '5xl': ['48px', { lineHeight: '1.1', letterSpacing: '-0.025em' }],
        '6xl': ['56px', { lineHeight: '1', letterSpacing: '-0.03em' }],
      },
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        // Ocean Sentinel Custom Colors - Mobile-First High Contrast
        ocean: {
          950: '#000814', // Fond ultra-sombre (contraste max)
          900: '#001d3d',
          800: '#003566',
          700: '#0353a4',
          600: '#0466c8',
          500: '#0582ca',
        },
        
        // Cloud White - Blanc nuageux doux
        'cloud-white': {
          DEFAULT: '#f0f4f8', // Blanc nuageux principal
          light: '#f8fafc',   // Blanc nuageux très clair
          dark: '#e2e8f0',    // Blanc nuageux foncé
        },
        
        // SACS Truth Badges (Règle de Vérité)
        'truth-measured': {
          DEFAULT: '#10b981', // Vert éclatant (MESURÉ - Capteur direct)
          dark: '#047857',
          light: '#34d399',
          contrast: '#ffffff', // Texte blanc sur vert
        },
        'truth-inferred': {
          DEFAULT: '#f59e0b', // Orange vif (INFÉRÉ - Proxy satellitaire)
          dark: '#d97706',
          light: '#fbbf24',
          contrast: '#000000', // Texte noir sur orange
        },
        'truth-simulated': {
          DEFAULT: '#6b7280', // Gris neutre (SIMULÉ - Modèle)
          dark: '#4b5563',
          light: '#9ca3af',
          contrast: '#ffffff', // Texte blanc sur gris
        },
        
        // Critical Alerts (Contraste maximum pour plein soleil)
        critical: {
          DEFAULT: '#dc2626', // Rouge vif (visible en extérieur)
          dark: '#991b1b',
          light: '#ef4444',
          bg: '#450a0a', // Fond rouge très sombre
          text: '#fecaca', // Texte rouge clair
          border: '#dc2626', // Bordure rouge vif
          glow: '#fee2e2', // Effet glow
        },
        
        // Success states
        success: {
          DEFAULT: '#10b981',
          dark: '#047857',
          light: '#34d399',
        },
        
        // Info/Accent (Cyan océanique)
        info: {
          DEFAULT: '#06b6d4', // Cyan vif
          dark: '#0891b2',
          light: '#22d3ee',
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
        "pulse-border": {
          "0%, 100%": { borderColor: "hsl(var(--destructive))" },
          "50%": { borderColor: "#ff6666" },
        },
        shimmer: {
          "0%": { backgroundPosition: "200% 0" },
          "100%": { backgroundPosition: "-200% 0" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
        "pulse-border": "pulse-border 2s infinite",
        shimmer: "shimmer 1.5s infinite",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
