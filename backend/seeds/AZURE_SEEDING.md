# Seeding Database in Azure Production

This guide explains how to run database seeding in Azure App Services production environment.

## Prerequisites

- Access to Azure Portal with appropriate permissions
- Backend App Service deployed and running
- Database connection configured in Azure App Service environment variables

## Method 1: Azure Portal SSH/Console (Recommended)

### Step-by-Step Instructions

1. **Navigate to Azure Portal**
   - Go to [portal.azure.com](https://portal.azure.com)
   - Sign in with your Azure credentials

2. **Find Your Backend App Service**
   - Search for your App Service name (e.g., "guess-the-worth-backend")
   - Click on the App Service to open it

3. **Open SSH/Console**
   - In the left sidebar, scroll to **Development Tools**
   - Click on **SSH** or **Console**
   - Wait for the terminal to load

4. **Navigate to Application Directory**
   ```bash
   cd /home/site/wwwroot
   ```

5. **Verify Environment**
   ```bash
   # Check Python is available
   python --version

   # Verify you're in the correct directory
   ls -la seeds/
   ```

6. **Run Seeding Script**
   ```bash
   python seeds/seed_manager.py --env production
   ```

7. **Confirm Seeding**
   - When prompted "Type 'yes' to continue:", type `yes` and press Enter
   - Wait for seeding to complete
   - You should see output like:
     ```
     🌱 Starting database seeding for environment: production
     ============================================================
     1️⃣  Seeding users...
        ✓ Created new user: Demo Admin
        ...
     ✅ Database seeding completed successfully!
     ```

## Method 2: Azure CLI (Alternative)

If you have Azure CLI installed locally:

```bash
# Login to Azure
az login

# Run command in App Service
az webapp ssh --name <your-backend-app-name> \
  --resource-group <your-resource-group> \
  --command "cd /home/site/wwwroot && python seeds/seed_manager.py --env production"
```

## Verification

After seeding, verify the data was created:

1. **Check via API**
   ```bash
   curl https://<your-backend-app-name>.azurewebsites.net/api/artworks
   ```

2. **Check Database Directly**
   - Use Azure Data Studio or pgAdmin
   - Connect to your Azure PostgreSQL instance
   - Query: `SELECT COUNT(*) FROM users;`

## Troubleshooting

### "role 'postgres' does not exist"
- **Issue**: Database connection not configured
- **Solution**: Check Azure App Service → Configuration → Application Settings
  - Verify `DATABASE_URL` is set correctly

### "Module not found"
- **Issue**: Dependencies not installed
- **Solution**: Rebuild and redeploy the backend container

### "Permission denied"
- **Issue**: SSH not enabled on App Service
- **Solution**:
  - Go to App Service → Configuration → General settings
  - Enable "SSH" under Platform settings
  - Restart the App Service

### Script doesn't exist
- **Issue**: Seeding files not included in deployment
- **Solution**: Verify the `seeds/` directory is copied in your Dockerfile (it is)

## Safety Features

The seeding script includes safety checks:
- ✅ **Environment verification** - Confirms target environment matches current environment
- ✅ **Production warning** - Requires explicit "yes" confirmation
- ✅ **Idempotency** - Safe to run multiple times without duplicating data
- ✅ **Rollback on error** - Database changes are rolled back if seeding fails

## When to Seed

**Recommended times to run production seeding:**
- Initial deployment (first time)
- After major demo resets
- For grading/presentation demos

**NOT recommended:**
- During active user sessions
- On every deployment (keep data persistent)
- If production already has real user data

## Seeded Data Summary

Running the seed script will create:
- **9 users** (1 admin, 3 sellers, 5 buyers)
- **15 artworks** (various categories and statuses)
- **27 bids** (realistic bidding history)

All demo accounts are documented in the main README.md.

## Alternative: One-Time Seeding via GitHub Actions

If you prefer to seed automatically on first deployment, you can add this to `.github/workflows/deploy-azure.yml`:

```yaml
- name: Seed production database (one-time)
  if: github.event.inputs.seed_database == 'true'
  run: |
    az webapp ssh --name ${{ secrets.AZURE_BACKEND_APP_NAME }} \
      --resource-group ${{ secrets.AZURE_RESOURCE_GROUP }} \
      --command "cd /home/site/wwwroot && python seeds/seed_manager.py --env production"
```

Then trigger manually via workflow_dispatch with seed_database input.

---

**Last Updated**: 2025-11-24
