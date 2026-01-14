#!/bin/bash

# Setup Cognito Frontend Client
# 🏆 Breaking Barriers UK 2026 compliant
#
# Creates a frontend-compatible Cognito User Pool Client without client secret
# for secure browser-based authentication using SRP (Secure Remote Password)
#
# Usage with environment variables:
#   export COGNITO_USER_POOL_ID="us-west-2_ASOPUuOOV"
#   export COGNITO_FRONTEND_CLIENT_ID="your-client-id"  # If already created
#   ./setup_cognito_frontend_client.sh

set -e

# Configuration from environment variables or defaults
USER_POOL_ID="${COGNITO_USER_POOL_ID:-us-west-2_ASOPUuOOV}"
CLIENT_NAME="${COGNITO_CLIENT_NAME:-ai-therapy-platform-frontend-client}"
REGION="${AWS_REGION:-us-west-2}"
EXISTING_CLIENT_ID="${COGNITO_FRONTEND_CLIENT_ID:-}"

# Callback URLs (update for production)
CALLBACK_URLS="http://localhost:3000,http://localhost:3000/auth/callback"
LOGOUT_URLS="http://localhost:3000,http://localhost:3000/auth/logout"

echo "🏆 Breaking Barriers UK 2026 - Cognito Frontend Client Setup"
echo "============================================================"
echo ""

# Check if client ID is already provided via environment variable
if [ -n "$EXISTING_CLIENT_ID" ]; then
    echo "✅ Using existing client ID from environment variable"
    echo "Client ID: $EXISTING_CLIENT_ID"
    CLIENT_ID="$EXISTING_CLIENT_ID"
else
    echo "Creating frontend-compatible Cognito client..."
    echo "User Pool ID: $USER_POOL_ID"
    echo "Client Name: $CLIENT_NAME"
    echo "Region: $REGION"
    echo ""
    
    # Check if AWS CLI is available and configured
    if ! command -v aws &> /dev/null; then
        echo "⚠️  AWS CLI not found. Please provide COGNITO_FRONTEND_CLIENT_ID environment variable"
        echo ""
        echo "Example:"
        echo "  export COGNITO_FRONTEND_CLIENT_ID='your-client-id'"
        echo "  ./setup_cognito_frontend_client.sh"
        exit 1
    fi
    
    # Try to create the client
    if CLIENT_OUTPUT=$(aws cognito-idp create-user-pool-client \
      --user-pool-id "$USER_POOL_ID" \
      --client-name "$CLIENT_NAME" \
      --no-generate-secret \
      --explicit-auth-flows "ALLOW_USER_SRP_AUTH" "ALLOW_REFRESH_TOKEN_AUTH" "ALLOW_CUSTOM_AUTH" \
      --supported-identity-providers "COGNITO" \
      --callback-urls "$CALLBACK_URLS" \
      --logout-urls "$LOGOUT_URLS" \
      --allowed-o-auth-flows "code" "implicit" \
      --allowed-o-auth-scopes "email" "openid" "profile" "aws.cognito.signin.user.admin" \
      --allowed-o-auth-flows-user-pool-client \
      --prevent-user-existence-errors ENABLED \
      --enable-token-revocation \
      --access-token-validity 1 \
      --id-token-validity 1 \
      --refresh-token-validity 30 \
      --token-validity-units AccessToken=hours,IdToken=hours,RefreshToken=days \
      --read-attributes "email" "email_verified" "custom:role" "custom:language_preference" \
      --write-attributes "email" "custom:role" "custom:language_preference" \
      --region "$REGION" \
      --output json 2>&1); then
        
        # Extract client ID
        CLIENT_ID=$(echo "$CLIENT_OUTPUT" | jq -r '.UserPoolClient.ClientId')
    else
        echo "⚠️  Failed to create Cognito client (not logged in or insufficient permissions)"
        echo ""
        echo "Please provide the client ID manually:"
        echo "  export COGNITO_FRONTEND_CLIENT_ID='your-client-id'"
        echo "  ./setup_cognito_frontend_client.sh"
        echo ""
        echo "Or create it in AWS Console:"
        echo "1. Go to Cognito User Pools"
        echo "2. Select pool: $USER_POOL_ID"
        echo "3. Create App Client with these settings:"
        echo "   - No client secret"
        echo "   - Auth flows: USER_SRP_AUTH, REFRESH_TOKEN_AUTH"
        echo "   - Token validity: 1h access, 1h ID, 30d refresh"
        exit 1
    fi
fi

echo ""
echo "✅ Frontend client configured successfully!"
echo ""
echo "================================================"
echo "IMPORTANT: Save these values for frontend setup"
echo "================================================"
echo ""
echo "Client ID: $CLIENT_ID"
echo "User Pool ID: $USER_POOL_ID"
echo "Region: $REGION"
echo ""
echo "Frontend Configuration:"
echo "----------------------"
echo "Update ai-therapy-frontend/src/config/aws-config.ts:"
echo ""
echo "cognito: {"
echo "  region: '$REGION',"
echo "  userPoolId: '$USER_POOL_ID',"
echo "  userPoolWebClientId: '$CLIENT_ID',"
echo "}"
echo ""
echo "================================================"
echo ""

# Save to file
cat > cognito-frontend-config.json <<EOF
{
  "region": "$REGION",
  "userPoolId": "$USER_POOL_ID",
  "userPoolWebClientId": "$CLIENT_ID",
  "clientName": "$CLIENT_NAME",
  "createdAt": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF

echo "✅ Configuration saved to: cognito-frontend-config.json"
echo ""
echo "Environment Variables (for future use):"
echo "export COGNITO_USER_POOL_ID='$USER_POOL_ID'"
echo "export COGNITO_FRONTEND_CLIENT_ID='$CLIENT_ID'"
echo "export AWS_REGION='$REGION'"
echo ""
echo "Next Steps:"
echo "1. Update frontend configuration with the Client ID above"
echo "2. Set USE_MOCK_AUTH = false in ai-therapy-frontend/src/services/auth.ts"
echo "3. Uncomment real Cognito code in auth.ts"
echo "4. Test user registration and login"
echo ""
echo "🏆 Breaking Barriers UK 2026 compliant setup complete!"
