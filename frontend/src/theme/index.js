import { createSystem, defaultConfig } from '@chakra-ui/react'

const customConfig = {
  ...defaultConfig,
  tokens: {
    colors: {
      primary: {
        50: '#e8f5f0',
        100: '#d1ebe1',
        200: '#a3d7c3',
        300: '#75c3a5',
        400: '#47af87',
        500: '#217C60',
        600: '#1a6350',
        700: '#134a3c',
        800: '#0d3128',
        900: '#061914',
      },
      accent: {
        50: '#fefce8',
        100: '#fef3c7',
        200: '#fde68a',
        300: '#fcd34d',
        400: '#cccc32',
        500: '#eab308',
        600: '#ca8a04',
        700: '#a16207',
        800: '#854d0e',
        900: '#713f12',
      },
      bg: {
        primary: '#FFFFFF',
        surface: '#f8fafc',
        surfaceLight: '#f1f5f9',
        dark: '#050315',
      },
      text: {
        primary: '#050315',
        light: '#FFFFFF',
        muted: '#64748b',
      }
    },
    gradients: {
      primary: 'linear-gradient(135deg, #217C60 0%, #cccc32 100%)',
      hero: 'radial-gradient(circle at 30% 20%, rgba(33, 124, 96, 0.15) 0%, transparent 50%), radial-gradient(circle at 70% 80%, rgba(204, 204, 50, 0.15) 0%, transparent 50%)',
    }
  },
  semanticTokens: {
    colors: {
      'text': '#050315',
      'text-light': '#FFFFFF', 
      'bg': '#FFFFFF',
      'primary': '#217C60',
      'accent': '#cccc32',
      'gradient.primary': 'linear-gradient(135deg, #217C60 0%, #cccc32 100%)',
    },
  },
  globalCss: {
    '*': {
      margin: 0,
      padding: 0,
      boxSizing: 'border-box',
    },
    'html, body': {
      fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
      lineHeight: 1.6,
      overflowX: 'hidden',
    },
    'body': {
      bg: 'bg',
      color: 'text',
      minHeight: '100vh',
    },
  },
}

export const system = createSystem(customConfig)