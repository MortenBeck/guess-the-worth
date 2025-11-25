# Seeding Database in Azure Production

This guide explains how to run database seeding in Azure App Services production environment.

## Prerequisites

- Access to Azure Portal with appropriate permissions
- Backend App Service deployed and running
- Database connection configured in Azure App Service environment variables

## Method 1: API Endpoint (Recommended - No SSH Required!)

The easiest way to seed your production database is via the admin API endpoint. This works even when Azure SSH is unavailable.

### Quick Start - Use the Helper Script

```bash
# From your local machine
cd backend/seeds

# Set your backend URL (replace with your actual URL)
export BACKEND_URL="https://your-backend-app.azurewebsites.net"

# Run the seeding script
./seed_production.sh
```

The script will:
1. Login with admin credentials
2. Trigger database seeding
3. Show you the results

### Manual Steps (If You Prefer)

1. **Get Admin Credentials**
   - Use the demo admin account: `admin@guesstheworth.com` / `AdminPass123!`
   - Or create your own admin user in the database

2. **Login to Get Access Token**
   ```bash
   # Replace with your actual backend URL
   BACKEND_URL="https://your-backend-app.azurewebsites.net"

   # Login and save the token
   TOKEN=$(curl -X POST "$BACKEND_URL/api/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"email": "admin@guesstheworth.com", "password": "AdminPass123!"}' \
     | jq -r '.access_token')

   echo "Token: $TOKEN"
   ```

3. **Trigger Database Seeding**
   ```bash
   curl -X POST "$BACKEND_URL/api/admin/seed-database?confirm=yes" \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json"
   ```

4. **Verify Success**
   You should see a response like:
   ```json
   {
     "success": true,
     "message": "Database seeded successfully",
     "summary": {
       "users": 9,
       "artworks": 15,
       "bids": 27
     }
   }
   ```

### Using Browser (Alternative)

1. Open your backend URL in a browser
2. Navigate to `/docs` (Swagger UI)
3. Click "Authorize" and login with admin credentials
4. Find `POST /api/admin/seed-database`
5. Click "Try it out"
6. Enter `yes` for the confirm parameter
7. Click "Execute"

## Method 2: Azure Portal SSH/Console (If SSH Works)

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

## Method 3: Azure CLI (Advanced)

**Note**: This method may not work if SSH is not configured in your Docker container.

If you have Azure CLI installed locally and SSH is properly configured:

```bash
# Login to Azure
az login

# Open interactive SSH session
az webapp ssh --name <your-backend-app-name> \
  --resource-group <your-resource-group>

# Then run inside the SSH session:
cd /home/site/wwwroot
python seeds/seed_manager.py --env production
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

### "SSH CONN CLOSE" or SSH Terminal Not Working
- **Issue**: Azure App Service SSH requires an SSH daemon in the container
- **Solution**: Use Method 1 (API endpoint) instead - it doesn't require SSH

### "401 Unauthorized" when calling API endpoint
- **Issue**: Token expired or invalid
- **Solution**: Login again to get a fresh token

### "403 Forbidden" when calling API endpoint
- **Issue**: User is not an admin
- **Solution**: Verify you're using an admin account (role must be "admin")

### "role 'postgres' does not exist"
- **Issue**: Database connection not configured
- **Solution**: Check Azure App Service → Configuration → Application Settings
  - Verify `DATABASE_URL` is set correctly

### "Module not found"
- **Issue**: Dependencies not installed
- **Solution**: Rebuild and redeploy the backend container

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
