export const config = {
  // API
  API_BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',

  // Auth0
  AUTH0_DOMAIN: import.meta.env.VITE_AUTH0_DOMAIN || 'guess-the-worth.eu.auth0.com',
  AUTH0_CLIENT_ID: import.meta.env.VITE_AUTH0_CLIENT_ID || 'M5WxOcqdtVR3PuEQrirdkMyQnpRMTtCI',
  AUTH0_AUDIENCE: import.meta.env.VITE_AUTH0_AUDIENCE || 'https://api.guesstheworth.com',

  // Socket.IO
  SOCKET_URL: import.meta.env.VITE_SOCKET_URL || 'http://localhost:8000',

  // Stripe
  STRIPE_PUBLISHABLE_KEY: import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY || '',

  // App
  APP_NAME: 'Guess The Worth',
  MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
};