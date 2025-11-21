# Azure Environment Variables Setup

## Backend App Service Configuration

Go to Azure Portal → Your Backend App Service → Configuration → Application settings

Add the following environment variables:

### Critical (Must Set):
```
CORS_ORIGINS=https://YOUR-FRONTEND-APP.azurewebsites.net,https://your-custom-domain.com
JWT_SECRET_KEY=generate-a-strong-random-secret-key-here
ENVIRONMENT=production
```

### Already Set:
```
DATABASE_URL=postgresql://gtw:5%M2TtBoJr54yHGN3b@gtw-database.postgres.database.azure.com:5432/postgres
SENTRY_DSN=your-sentry-dsn-here
```

### Optional (if using):
```
STRIPE_SECRET_KEY=sk_live_your_stripe_secret
STRIPE_PUBLISHABLE_KEY=pk_live_your_stripe_publishable
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
```

## Frontend App Service Configuration

Go to Azure Portal → Your Frontend App Service → Configuration → Application settings

The frontend build-time variables are already set in the GitHub workflow, but verify:

```
VITE_API_BASE_URL=https://YOUR-BACKEND-APP.azurewebsites.net
VITE_SOCKET_URL=https://YOUR-BACKEND-APP.azurewebsites.net
VITE_AUTH0_DOMAIN=guess-the-worth.eu.auth0.com
VITE_AUTH0_CLIENT_ID=M5WxOcqdtVR3PuEQrirdkMyQnpRMTtCI
VITE_AUTH0_AUDIENCE=https://api.guesstheworth.com
VITE_SENTRY_DSN=your-frontend-sentry-dsn
```

## How to Generate JWT_SECRET_KEY

Run this in your terminal:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Or:
```bash
openssl rand -base64 32
```

## CORS_ORIGINS Format

Make sure to include:
- Your Azure frontend URL: `https://your-frontend-app.azurewebsites.net`
- Any custom domains
- Separate multiple origins with commas (no spaces)

Example:
```
CORS_ORIGINS=https://gtw-frontend.azurewebsites.net,https://guesstheworth.com,https://www.guesstheworth.com
```

## After Setting Environment Variables

1. Save the configuration in Azure Portal
2. Azure will automatically restart your app
3. Check the logs in Log Stream to verify the app starts successfully
