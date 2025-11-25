#!/bin/bash
# Helper script to seed production database via API endpoint
# No SSH required!

set -e

# Configuration
BACKEND_URL="${BACKEND_URL:-https://your-backend-app.azurewebsites.net}"
ADMIN_EMAIL="${ADMIN_EMAIL:-admin@guesstheworth.com}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-AdminPass123!}"
BOOTSTRAP_TOKEN="${BOOTSTRAP_TOKEN:-TEMP_SEED_2024_REMOVE_AFTER_USE}"

echo "🌱 Production Database Seeding Script"
echo "======================================"
echo ""
echo "Backend URL: $BACKEND_URL"
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

# Try bootstrap token first (for empty database)
echo "🔐 Attempting bootstrap seeding (for empty database)..."
SEED_RESPONSE=$(curl -s -X POST "$BACKEND_URL/api/admin/seed-database?confirm=yes&bootstrap_token=$BOOTSTRAP_TOKEN" \
  -H "Content-Type: application/json")

# Check if bootstrap succeeded
if command -v jq &> /dev/null; then
    SUCCESS=$(echo "$SEED_RESPONSE" | jq -r '.success' 2>/dev/null || echo "null")
else
    if echo "$SEED_RESPONSE" | grep -q '"success":true'; then
        SUCCESS="true"
    else
        SUCCESS="null"
    fi
fi

if [ "$SUCCESS" = "true" ]; then
    echo "✅ Bootstrap seeding successful!"
    if command -v jq &> /dev/null; then
        echo "$SEED_RESPONSE" | jq '.'
    else
        echo "$SEED_RESPONSE"
    fi
    echo ""
    echo "⚠️  IMPORTANT: Bootstrap token used for initial seeding."
    echo "   The admin account has been created: $ADMIN_EMAIL"
    echo "   You can now login with this account for future seeding."
    exit 0
fi

# Bootstrap failed, try normal authentication
echo "⚠️  Bootstrap token not valid (database not empty or token disabled)."
echo "🔐 Attempting login with admin credentials..."
echo "   Email: $ADMIN_EMAIL"
echo ""

LOGIN_RESPONSE=$(curl -s -X POST "$BACKEND_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$ADMIN_EMAIL\", \"password\": \"$ADMIN_PASSWORD\"}")

if command -v jq &> /dev/null; then
    TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token' 2>/dev/null || echo "")
    if [ "$TOKEN" = "null" ] || [ -z "$TOKEN" ]; then
        echo "❌ Login failed!"
        echo "$LOGIN_RESPONSE" | jq '.' 2>/dev/null || echo "$LOGIN_RESPONSE"
        exit 1
    fi
else
    # Fallback if jq is not available
    TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4 || echo "")
    if [ -z "$TOKEN" ]; then
        echo "❌ Login failed!"
        echo "$LOGIN_RESPONSE"
        exit 1
    fi
fi

echo "✅ Login successful!"
echo ""

# Seed database with authentication
echo "🌱 Triggering database seeding..."
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
