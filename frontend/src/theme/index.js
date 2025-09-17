import { createSystem, defaultConfig } from '@chakra-ui/react'

const customConfig = {
  ...defaultConfig,
  semanticTokens: {
    colors: {
      'text': '#050315',
      'text-light': '#FFFFFF',
      'bg': '#FFFFFF',
      'primary': '#217C60',
      'accent': '#cccc32',
    },
  },
}

export const system = createSystem(customConfig)