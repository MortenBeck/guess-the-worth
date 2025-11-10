# Azure Deployment Setup Guide

This guide explains how to set up and deploy the Guess The Worth application to Azure.

## Azure Resources Needed

### 1. Azure Database for PostgreSQL
- Go to Azure Portal → Create a resource → Azure Database for PostgreSQL
- Choose "Flexible Server" (recommended for cost control)
- Configuration:
  - **Compute tier**: Burstable (B1ms for development)
  - **Storage**: 32 GB (can start small)
  - **Backup retention**: 7 days
  - **High availability**: Disabled (save costs)
- Note the connection string format:
  ```
  postgresql://username:password@servername.postgres.database.azure.com:5432/databasename?sslmode=require
  ```

### 2. Azure App Service (Backend)
- Go to Azure Portal → Create a resource → Web App
- Configuration:
  - **Publish**: Docker Container
  - **Operating System**: Linux
  - **Region**: Choose closest to your users
  - **Pricing tier**: B1 (Basic) or F1 (Free) for testing
- Container settings:
  - **Image Source**: GitHub Container Registry (GHCR)
  - **Image**: `ghcr.io/yourusername/guess-the-worth/backend:latest`
  - **Registry**: `ghcr.io`
- Application Settings (Environment Variables):
  ```
  DATABASE_URL=<your-postgresql-connection-string>
  SECRET_KEY=<generate-a-secure-random-string>
  ALGORITHM=HS256
  ACCESS_TOKEN_EXPIRE_MINUTES=30
  AUTH0_DOMAIN=<your-auth0-domain>
  AUTH0_AUDIENCE=<your-auth0-audience>
  AUTH0_CLIENT_ID=<your-auth0-client-id>
  AUTH0_CLIENT_SECRET=<your-auth0-client-secret>
  CORS_ORIGINS=https://<your-frontend-app-name>.azurewebsites.net
  ```

### 3. Azure App Service (Frontend)
- Go to Azure Portal → Create a resource → Web App
- Configuration:
  - **Publish**: Code
  - **Runtime stack**: Node 20 LTS
  - **Operating System**: Linux
  - **Region**: Sweden Central (same as backend for lower latency)
  - **Pricing tier**: F1 (Free) or B1 (Basic)
- Application Settings (Environment Variables):
  ```
  NODE_ENV=production
  ```
- Note: Frontend environment variables (VITE_*) are baked into the build during CI/CD

## GitHub Authentication Setup

### Step 1: Create Managed Identity for GitHub Actions

1. In Azure Portal, search for **"Managed Identities"**
2. Click **+ Create**
   - **Subscription**: Your subscription
   - **Resource group**: Same as your App Services
   - **Region**: Sweden Central (match your resources)
   - **Name**: `github-actions-identity`
3. Click **Review + Create** → **Create**

### Step 2: Configure Federated Credentials

1. Go to the managed identity you just created
2. Navigate to **Settings** → **Federated credentials**
3. Click **+ Add credential**:
   - **Federated credential scenario**: GitHub Actions deploying Azure resources
   - **Organization**: Your GitHub username
   - **Repository**: `guess-the-worth`
   - **Entity type**: Branch
   - **GitHub branch name**: `main`
   - **Name**: `main-branch-deployer`
4. Click **Add**

### Step 3: Grant Permissions

1. Go to your **Resource Group** (containing all your resources)
2. Click **Access control (IAM)**
3. Click **+ Add** → **Add role assignment**
4. Select **Contributor** role → Click **Next**
5. Click **+ Select members** → Search for `github-actions-identity`
6. Click **Review + assign**

### Step 4: Get Required Values

Run these commands in Azure Cloud Shell:

```bash
# Get your subscription ID
az account show --query id -o tsv

# Get your tenant ID
az account show --query tenantId -o tsv

# Get the client ID of the managed identity
az identity show --name github-actions-identity --resource-group <your-resource-group-name> --query clientId -o tsv
```

## GitHub Secrets Configuration

Add these secrets to your GitHub repository (Settings → Secrets and variables → Actions):

### Required Secrets

1. **AZURE_CLIENT_ID**: The client ID from the managed identity (output from command above)

2. **AZURE_TENANT_ID**: Your Azure tenant ID (output from command above)

3. **AZURE_SUBSCRIPTION_ID**: Your Azure subscription ID (output from command above)

4. **AZURE_BACKEND_APP_NAME**: Your App Service name (e.g., `guess-the-worth-backend`)

5. **AZURE_BACKEND_URL**: Your backend URL (e.g., `https://guess-the-worth-backend.azurewebsites.net`)

6. **AZURE_FRONTEND_APP_NAME**: Your frontend App Service name (e.g., `guess-the-worth-frontend`)

7. **VITE_AUTH0_DOMAIN**: Your Auth0 domain

8. **VITE_AUTH0_CLIENT_ID**: Your Auth0 client ID

9. **VITE_AUTH0_AUDIENCE**: Your Auth0 API audience

10. **CODECOV_TOKEN**: Your Codecov token (already configured)

## Initial Deployment Steps

### 1. Create Azure Resources
Follow the sections above to create:
- PostgreSQL database
- App Service for backend (Docker container)
- App Service for frontend (Node.js)

### 2. Set Up GitHub Actions Authentication
Follow the **GitHub Authentication Setup** section above to:
- Create a managed identity for GitHub Actions
- Configure federated credentials for OIDC authentication
- Grant contributor permissions to the managed identity
- Add required secrets to GitHub repository

### 3. Configure GHCR Access for Backend App Service
The backend App Service needs to pull Docker images from GitHub Container Registry:

1. Generate a GitHub Personal Access Token:
   - Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Click **Generate new token (classic)**
   - Grant `read:packages` permission
   - Copy the token (you won't see it again)

2. Configure backend App Service:
   - Go to Azure Portal → Your Backend App Service
   - Navigate to **Settings** → **Configuration**
   - Under **Container settings**:
     - **Registry server URL**: `https://ghcr.io`
     - **Registry username**: Your GitHub username (lowercase)
     - **Registry password**: The GitHub PAT you generated
   - Click **Save**

### 4. Run Database Migrations
After first deployment, run migrations:

Option A - Using Azure CLI:
```bash
az webapp ssh --name <your-app-name> --resource-group <your-rg>
# Once connected:
cd /home/site/wwwroot
python -m alembic upgrade head
```

Option B - Using Azure Portal:
1. Go to App Service → SSH → Go
2. Navigate to app directory
3. Run: `python -m alembic upgrade head`

### 5. Configure Auth0
Update your Auth0 application settings:
- Add frontend App Service URL (e.g., `https://guess-the-worth-frontend.azurewebsites.net`) to **Allowed Callback URLs**
- Add frontend App Service URL to **Allowed Web Origins**
- Add frontend App Service URL to **Allowed Logout URLs**

## Cost Management

Since you're using on/off approach to save credits:

### Stopping Services
```bash
# Stop backend App Service
az webapp stop --name <backend-app-name> --resource-group <resource-group-name>

# Stop frontend App Service
az webapp stop --name <frontend-app-name> --resource-group <resource-group-name>

# Stop PostgreSQL (note: billing continues for storage)
az postgres flexible-server stop --name <db-server-name> --resource-group <resource-group-name>
```

### Starting Services
```bash
# Start PostgreSQL first
az postgres flexible-server start --name <db-server-name> --resource-group <resource-group-name>

# Then start backend App Service
az webapp start --name <backend-app-name> --resource-group <resource-group-name>

# Start frontend App Service
az webapp start --name <frontend-app-name> --resource-group <resource-group-name>

# Wait ~30 seconds for cold start, then verify health
curl https://<backend-app-name>.azurewebsites.net/health
curl https://<frontend-app-name>.azurewebsites.net
```

### Auto-pause Configuration
For Azure Database for PostgreSQL Flexible Server:
- Enable "Auto-pause" in Configuration
- Set delay (e.g., 60 minutes of inactivity)
- Database will auto-resume when App Service connects

## Monitoring

### Health Check Endpoints
- Backend: `https://<backend-app-name>.azurewebsites.net/health`
- Backend DB: `https://<backend-app-name>.azurewebsites.net/health/db`

### Azure Portal Monitoring
- App Service → Monitoring → Metrics
- PostgreSQL → Monitoring → Metrics
- Set up alerts for high resource usage

## Troubleshooting

### Container won't pull from GHCR
- Verify GitHub PAT has `read:packages` permission
- Check container registry credentials in App Service settings
- Ensure image name is lowercase: `ghcr.io/username/repo:tag`

### Database connection errors
- Check firewall rules in PostgreSQL → Networking
- Add "Allow Azure services" rule
- Verify connection string includes `?sslmode=require`

### Frontend can't reach backend
- Check CORS settings in backend environment variables (must include frontend URL)
- Verify `VITE_API_BASE_URL` was set correctly during build (check GitHub Actions logs)
- Check if both App Services are running (not stopped)
- Test backend directly: `curl https://backend-app-name.azurewebsites.net/health`

### Cold start is slow
- This is normal for B1/Free tier App Services
- First request after stop can take 30-60 seconds
- Consider keeping services running during active development

## Next Steps

After deployment:
1. Test the health endpoints
2. Verify database migrations ran successfully
3. Test user authentication flow
4. Create your first artwork to verify end-to-end functionality
5. Monitor costs in Azure Cost Management

## Deployment Workflow

The deployment happens automatically when you push to `main`:
1. Backend CI builds and pushes Docker image to GHCR
2. Deploy workflow pulls image and deploys backend to App Service
3. Frontend builds with production env vars (from GitHub secrets)
4. Frontend deploys to frontend App Service as a Node.js application

To manually trigger deployment:
- Go to GitHub Actions → Deploy to Azure → Run workflow
