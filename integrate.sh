#!/bin/bash

# AI Therapy Platform - Frontend-Backend Integration Script
# 🏆 Breaking Barriers UK 2026 compliant
#
# This script automates the integration of frontend and backend
#
# Usage with environment variables (if not logged in to AWS):
#   export COGNITO_USER_POOL_ID="us-west-2_ASOPUuOOV"
#   export COGNITO_FRONTEND_CLIENT_ID="your-client-id"
#   export AWS_REGION="us-west-2"
#   ./integrate.sh

set -e

echo "🏆 Breaking Barriers UK 2026 - AI Therapy Platform Integration"
echo "=============================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "ai-therapy-frontend" ]; then
    echo -e "${RED}Error: Please run this script from the project root directory${NC}"
    exit 1
fi

# Default values
DEFAULT_USER_POOL_ID="us-west-2_ASOPUuOOV"
DEFAULT_REGION="us-west-2"
DEFAULT_API_URL="https://yqv4v90gj9.execute-api.us-west-2.amazonaws.com/dev"
DEFAULT_WS_URL="wss://yqv4v90gj9.execute-api.us-west-2.amazonaws.com/dev"

echo "Step 1: Setting up Cognito Frontend Client"
echo "==========================================="
echo ""

# Check if environment variables are set
if [ -n "$COGNITO_FRONTEND_CLIENT_ID" ]; then
    echo -e "${GREEN}✅ Using Cognito configuration from environment variables${NC}"
    CLIENT_ID="$COGNITO_FRONTEND_CLIENT_ID"
    USER_POOL_ID="${COGNITO_USER_POOL_ID:-$DEFAULT_USER_POOL_ID}"
    REGION="${AWS_REGION:-$DEFAULT_REGION}"
    
    echo "Client ID: $CLIENT_ID"
    echo "User Pool ID: $USER_POOL_ID"
    echo "Region: $REGION"
    echo ""
    
    # Create config file
    cat > backend/cognito-frontend-config.json <<EOF
{
  "region": "$REGION",
  "userPoolId": "$USER_POOL_ID",
  "userPoolWebClientId": "$CLIENT_ID",
  "clientName": "ai-therapy-platform-frontend-client",
  "createdAt": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF
    
else
    echo -e "${YELLOW}⚠️  No COGNITO_FRONTEND_CLIENT_ID environment variable found${NC}"
    echo "Attempting to create Cognito client with AWS CLI..."
    echo ""
    
    cd backend
    chmod +x scripts/setup_cognito_frontend_client.sh
    
    if ./scripts/setup_cognito_frontend_client.sh; then
        echo -e "${GREEN}✅ Cognito client created successfully${NC}"
    else
        echo -e "${RED}❌ Failed to create Cognito client${NC}"
        echo ""
        echo "Please set environment variables manually:"
        echo ""
        echo "  export COGNITO_USER_POOL_ID='us-west-2_ASOPUuOOV'"
        echo "  export COGNITO_FRONTEND_CLIENT_ID='your-client-id'"
        echo "  export AWS_REGION='us-west-2'"
        echo ""
        echo "Then run this script again: ./integrate.sh"
        echo ""
        echo "To get a client ID:"
        echo "1. Go to AWS Console > Cognito > User Pools"
        echo "2. Select pool: us-west-2_ASOPUuOOV"
        echo "3. Create App Client (no secret, SRP auth)"
        echo "4. Copy the Client ID"
        exit 1
    fi
    
    cd ..
    
    # Check if config file was created
    if [ ! -f "backend/cognito-frontend-config.json" ]; then
        echo -e "${RED}Error: Cognito configuration not created${NC}"
        exit 1
    fi
    
    # Extract values
    CLIENT_ID=$(jq -r '.userPoolWebClientId' backend/cognito-frontend-config.json)
    USER_POOL_ID=$(jq -r '.userPoolId' backend/cognito-frontend-config.json)
    REGION=$(jq -r '.region' backend/cognito-frontend-config.json)
fi

echo "Step 2: Updating Frontend Configuration"
echo "========================================"
echo ""

# Update aws-config.ts
AWS_CONFIG_FILE="ai-therapy-frontend/src/config/aws-config.ts"

if [ -f "$AWS_CONFIG_FILE" ]; then
    # Backup original
    cp "$AWS_CONFIG_FILE" "${AWS_CONFIG_FILE}.backup"
    
    # Update configuration
    sed -i.tmp "s/userPoolWebClientId: '.*'/userPoolWebClientId: '$CLIENT_ID'/" "$AWS_CONFIG_FILE"
    rm "${AWS_CONFIG_FILE}.tmp" 2>/dev/null || true
    
    echo -e "${GREEN}✅ Updated aws-config.ts${NC}"
else
    echo -e "${YELLOW}⚠️  Warning: aws-config.ts not found${NC}"
fi

echo ""

echo "Step 3: Enabling Real Authentication"
echo "====================================="
echo ""

AUTH_SERVICE_FILE="ai-therapy-frontend/src/services/auth.ts"

if [ -f "$AUTH_SERVICE_FILE" ]; then
    # Backup original
    cp "$AUTH_SERVICE_FILE" "${AUTH_SERVICE_FILE}.backup"
    
    # Change USE_MOCK_AUTH to false
    sed -i.tmp 's/const USE_MOCK_AUTH = true/const USE_MOCK_AUTH = false/' "$AUTH_SERVICE_FILE"
    rm "${AUTH_SERVICE_FILE}.tmp" 2>/dev/null || true
    
    echo -e "${GREEN}✅ Enabled real authentication${NC}"
else
    echo -e "${YELLOW}⚠️  Warning: auth.ts not found${NC}"
fi

echo ""

echo "Step 4: Creating Environment Files"
echo "==================================="
echo ""

# Use environment variables or defaults
API_URL="${API_GATEWAY_URL:-$DEFAULT_API_URL}"
WS_URL="${WEBSOCKET_URL:-$DEFAULT_WS_URL}"

# Create backend .env
cat > backend/.env <<EOF
AWS_REGION=$REGION
COGNITO_USER_POOL_ID=$USER_POOL_ID
COGNITO_CLIENT_ID=$CLIENT_ID
USERS_TABLE_NAME=ai-therapy-platform-dev-users
SESSIONS_TABLE_NAME=ai-therapy-platform-dev-sessions
RED_FLAGS_TABLE_NAME=ai-therapy-platform-dev-redflags
NOTIFICATIONS_TABLE_NAME=ai-therapy-platform-dev-notifications
WEBSOCKET_API_ENDPOINT=$WS_URL
API_GATEWAY_URL=$API_URL
EOF

echo -e "${GREEN}✅ Created backend/.env${NC}"

# Create frontend .env.local
cat > ai-therapy-frontend/.env.local <<EOF
NEXT_PUBLIC_AWS_REGION=$REGION
NEXT_PUBLIC_COGNITO_USER_POOL_ID=$USER_POOL_ID
NEXT_PUBLIC_COGNITO_CLIENT_ID=$CLIENT_ID
NEXT_PUBLIC_API_URL=$API_URL
NEXT_PUBLIC_WEBSOCKET_URL=$WS_URL
EOF

echo -e "${GREEN}✅ Created ai-therapy-frontend/.env.local${NC}"

echo ""

echo "Step 5: Installing Dependencies"
echo "================================"
echo ""

# Install frontend dependencies
cd ai-therapy-frontend
if [ -f "package.json" ]; then
    echo "Installing frontend dependencies..."
    npm install
    echo -e "${GREEN}✅ Frontend dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠️  Warning: package.json not found${NC}"
fi

cd ..

echo ""
echo "=============================================================="
echo -e "${GREEN}✅ Integration Complete!${NC}"
echo "=============================================================="
echo ""
echo "Configuration Summary:"
echo "---------------------"
echo "Region: $REGION"
echo "User Pool ID: $USER_POOL_ID"
echo "Client ID: $CLIENT_ID"
echo "API URL: $API_URL"
echo "WebSocket URL: $WS_URL"
echo ""
echo "Environment Variables (save these for future use):"
echo "--------------------------------------------------"
echo "export COGNITO_USER_POOL_ID='$USER_POOL_ID'"
echo "export COGNITO_FRONTEND_CLIENT_ID='$CLIENT_ID'"
echo "export AWS_REGION='$REGION'"
echo "export API_GATEWAY_URL='$API_URL'"
echo "export WEBSOCKET_URL='$WS_URL'"
echo ""
echo "Next Steps:"
echo "----------"
echo "1. Start the frontend:"
echo "   cd ai-therapy-frontend"
echo "   npm run dev"
echo ""
echo "2. Open http://localhost:3000"
echo ""
echo "3. Test the integration:"
echo "   - Register a new user"
echo "   - Login with credentials"
echo "   - Start a therapy session"
echo "   - Check therapist dashboard"
echo "   - Check admin dashboard"
echo ""
echo "Manual Steps Required:"
echo "---------------------"
echo "1. Uncomment real API code in frontend files:"
echo "   - src/services/auth.ts"
echo "   - src/services/api.ts"
echo "   - src/services/websocket.ts"
echo "   - src/components/TherapistDashboard.tsx"
echo "   - src/components/AdminDashboard.tsx"
echo ""
echo "2. Deploy backend API endpoints:"
echo "   cd backend"
echo "   python3 scripts/package_lambdas.py"
echo "   cd ../terraform"
echo "   terraform apply"
echo ""
echo "For detailed instructions, see:"
echo "FRONTEND_BACKEND_INTEGRATION_GUIDE.md"
echo ""
echo "🏆 Breaking Barriers UK 2026 compliant setup complete!"
