# Azure Deployment Setup - Continue from Authentication Configuration

**Project**: Guess The Worth - Auction/bidding web application
**Stack**: FastAPI backend, React frontend, PostgreSQL database
**Current Branch**: `cicd-pipeline`

---

## WHAT HAS BEEN COMPLETED

### ✅ Phases 1-6: Full CI/CD Pipeline
- Backend CI: Linting (Black, flake8, isort), testing, security (Bandit, pip-audit, TruffleHog, Trivy), Docker builds
- Frontend CI: Linting (ESLint, Prettier), testing, security (npm audit), builds
- GHCR integration: Docker images pushed to GitHub Container Registry on main branch
- Codecov integration: Coverage reports on PRs (0% threshold by design)
- Branch protection: All CI checks must pass before merging to main

### ✅ Phase 7 - Azure Infrastructure Created
User has created these Azure resources:
- Resource Group (containing all resources)
- Azure Database for PostgreSQL Flexible Server (Sweden Central, B1ms tier)
- Backend App Service (Docker container, Linux)
- Frontend App Service (Node 20 LTS, Linux)
- Managed Identity: `github-actions-identity`
  - Federated credentials configured for GitHub Actions on `main` branch
  - Contributor role assigned to resource group

### ✅ Phase 7 - Code Changes Completed
1. **Health endpoints** (`backend/routers/health.py`):
   - `/health` - Basic health check
   - `/health/db` - Database connectivity check

2. **Azure-optimized database pooling** (`backend/database.py`):
   - QueuePool for Azure PostgreSQL (detects Azure connection string)
   - NullPool for local development
   - Handles cold starts and connection recycling

3. **Frontend Express server** (`frontend/server.js`):
   - Serves built React app from `dist/`
   - Handles client-side routing (SPA)
   - Port 8080 (Azure default)

4. **Frontend error handling** (`frontend/src/services/api.js`):
   - Graceful handling when backend is offline
   - User-friendly error messages

5. **Deployment workflow** (`.github/workflows/deploy-azure.yml`):
   - OIDC authentication with managed identity
   - Backend: Pulls Docker image from GHCR, deploys to App Service
   - Frontend: Builds with VITE_* env vars, deploys as Node.js app
   - Health checks after deployment

6. **Documentation** (`AZURE_SETUP.md`):
   - Complete setup guide
   - Cost management commands (start/stop services)
   - Troubleshooting section

---

## WHERE WE ARE NOW

**STUCK AT**: Configuring authentication for GitHub Actions to deploy to Azure

**Why OIDC with Managed Identity**:
- Azure Student account can't create service principals (directory permission restriction)
- Basic authentication disabled (can't download publish profiles)
- OIDC is the modern, recommended approach

**What's Been Done**:
1. ✅ Created managed identity: `github-actions-identity`
2. ✅ Configured federated credentials for GitHub Actions
3. ✅ Assigned Contributor role to managed identity (found in "Privileged administrator roles" tab)
4. ⚠️ **CURRENTLY HERE**: Need to get Azure values and configure GitHub secrets

---

## WHAT NEEDS TO BE DONE

### Step 1: Get Azure Values from Cloud Shell

Run these commands in Azure Cloud Shell (one at a time):

```bash
# Get subscription ID
az account show --query id -o tsv

# Get tenant ID
az account show --query tenantId -o tsv

# Get client ID of managed identity (replace <resource-group-name> with actual name)
az identity show --name github-actions-identity --resource-group <resource-group-name> --query clientId -o tsv
```

Save all three outputs - needed for GitHub secrets.

### Step 2: Create GitHub Personal Access Token

For backend to pull Docker images from GHCR:
1. GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token with `read:packages` permission
3. Copy token (starts with `ghp_...`)

### Step 3: Configure Backend Container Settings

Azure Portal → Backend App Service → Settings → Configuration → **Container settings tab**:
- Registry server URL: `https://ghcr.io`
- Registry username: GitHub username (lowercase)
- Registry password: GitHub PAT from Step 2
- Click Save

### Step 4: Add GitHub Secrets

GitHub repo → Settings → Secrets and variables → Actions → New repository secret

Add these 9 secrets:
- `AZURE_CLIENT_ID` (from Step 1, command 3)
- `AZURE_TENANT_ID` (from Step 1, command 2)
- `AZURE_SUBSCRIPTION_ID` (from Step 1, command 1)
- `AZURE_BACKEND_APP_NAME` (your backend App Service name)
- `AZURE_BACKEND_URL` (https://your-backend-name.azurewebsites.net)
- `AZURE_FRONTEND_APP_NAME` (your frontend App Service name)
- `VITE_AUTH0_DOMAIN` (from Auth0 dashboard)
- `VITE_AUTH0_CLIENT_ID` (from Auth0 dashboard)
- `VITE_AUTH0_AUDIENCE` (from Auth0 dashboard)

Note: `CODECOV_TOKEN` already exists.

### Step 5: Configure Backend App Service Environment Variables

Azure Portal → Backend App Service → Settings → Configuration → Application settings

Add these variables:
- `DATABASE_URL` (PostgreSQL connection string)
- `SECRET_KEY` (generate random secure string)
- `ALGORITHM=HS256`
- `ACCESS_TOKEN_EXPIRE_MINUTES=30`
- `AUTH0_DOMAIN` (from Auth0)
- `AUTH0_AUDIENCE` (from Auth0)
- `AUTH0_CLIENT_ID` (from Auth0)
- `AUTH0_CLIENT_SECRET` (from Auth0)
- `CORS_ORIGINS` (https://your-frontend-name.azurewebsites.net)

### Step 6: Test Deployment

1. Commit and push to `cicd-pipeline` branch
2. Wait for CI to pass
3. Create PR to main
4. Merge PR
5. Watch "Deploy to Azure" workflow run
6. Test: `https://your-backend-name.azurewebsites.net/health`

### Step 7: Run Database Migrations

After first deployment:
```bash
az webapp ssh --name <backend-app-name> --resource-group <resource-group-name>
cd /home/site/wwwroot
python -m alembic upgrade head
```

### Step 8: Configure Auth0

Add frontend URL to Auth0 application:
- Allowed Callback URLs
- Allowed Web Origins
- Allowed Logout URLs

---

## IMPORTANT NOTES

1. **Azure Student Limitations**: Can't create service principals or use basic auth, so using OIDC
2. **Cost Management**: Start/stop services to save credits (commands in AZURE_SETUP.md)
3. **Container Settings**: Must be in Configuration → Container settings **tab** (not main page)
4. **Contributor Role**: Found in "Privileged administrator roles" tab in Azure Portal
5. **User Handles Git**: Don't auto-commit unless explicitly requested

---

## WHAT TO DO NEXT

Continue from Step 1 above. Ask the user which step they're on or need help with.
