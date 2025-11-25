#!/bin/bash
# Helper script to seed production database via API endpoint
# No SSH required!

set -e

# Configuration
BACKEND_URL="${BACKEND_URL:-https://your-backend-app.azurewebsites.net}"
ADMIN_EMAIL="${ADMIN_EMAIL:-admin@guesstheworth.com}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-AdminPass123!}"

echo "🌱 Production Database Seeding Script"
echo "======================================"
echo ""
echo "Backend URL: $BACKEND_URL"
echo "Admin Email: $ADMIN_EMAIL"
echo ""

# Check for required tools
if ! command -v curl &> /dev/null; then
    echo "❌ Error: curl is required but not installed"
    exit 1
fi

if ! command -v jq &> /dev/null; then
    echo "⚠️  Warning: jq is not installed. Install it for better output formatting."
    echo "   On macOS: brew install jq"
    echo "   On Ubuntu: sudo apt-get install jq"
    echo ""
fi

# Step 1: Login
echo "🔐 Step 1: Logging in as admin..."
LOGIN_RESPONSE=$(curl -s -X POST "$BACKEND_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$ADMIN_EMAIL\", \"password\": \"$ADMIN_PASSWORD\"}")

if command -v jq &> /dev/null; then
    TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token')
    if [ "$TOKEN" = "null" ] || [ -z "$TOKEN" ]; then
        echo "❌ Login failed!"
        echo "$LOGIN_RESPONSE" | jq '.'
        exit 1
    fi
else
    # Fallback if jq is not available
    TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
    if [ -z "$TOKEN" ]; then
        echo "❌ Login failed!"
        echo "$LOGIN_RESPONSE"
        exit 1
    fi
fi

echo "✅ Login successful!"
echo ""

# Step 2: Seed database
echo "🌱 Step 2: Triggering database seeding..."
echo ""
SEED_RESPONSE=$(curl -s -X POST "$BACKEND_URL/api/admin/seed-database?confirm=yes" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")

if command -v jq &> /dev/null; then
    echo "$SEED_RESPONSE" | jq '.'
    SUCCESS=$(echo "$SEED_RESPONSE" | jq -r '.success')
    if [ "$SUCCESS" = "true" ]; then
        echo ""
        echo "✅ Database seeding completed successfully!"
        exit 0
    else
        echo ""
        echo "❌ Seeding failed!"
        exit 1
    fi
else
    echo "$SEED_RESPONSE"
    if echo "$SEED_RESPONSE" | grep -q '"success":true'; then
        echo ""
        echo "✅ Database seeding completed successfully!"
        exit 0
    else
        echo ""
        echo "❌ Seeding failed!"
        exit 1
    fi
fi
