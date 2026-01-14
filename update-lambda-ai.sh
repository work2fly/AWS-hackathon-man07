#!/bin/bash
# Update Lambda function with AI-enabled handler
# 🏆 Breaking Barriers UK 2026 compliant

set -e

echo "🚀 Updating Lambda function with Bedrock AI integration..."

# Get Lambda function name from environment or use default
LAMBDA_FUNCTION_NAME="${LAMBDA_FUNCTION_NAME:-ai-therapy-platform-dev-websocket-default}"

# Check if function exists
if ! aws lambda get-function --function-name "$LAMBDA_FUNCTION_NAME" --region us-west-2 > /dev/null 2>&1; then
    echo "❌ Lambda function not found: $LAMBDA_FUNCTION_NAME"
    echo "Please set LAMBDA_FUNCTION_NAME environment variable"
    exit 1
fi

echo "📦 Creating deployment package..."
cd backend
zip -q websocket_default_simple.zip websocket_default_simple.py

echo "⬆️  Uploading to Lambda..."
aws lambda update-function-code \
    --function-name "$LAMBDA_FUNCTION_NAME" \
    --zip-file fileb://websocket_default_simple.zip \
    --region us-west-2

echo "⏳ Waiting for update to complete..."
aws lambda wait function-updated \
    --function-name "$LAMBDA_FUNCTION_NAME" \
    --region us-west-2

# Clean up
rm websocket_default_simple.zip
cd ..

echo "✅ Lambda function updated successfully!"
echo ""
echo "🎯 Next steps:"
echo "1. Hard refresh your browser (Cmd+Shift+R or Ctrl+Shift+R)"
echo "2. Start a session"
echo "3. Type a message in the chat"
echo "4. Get AI therapy responses powered by Bedrock!"
echo ""
echo "🏆 Breaking Barriers UK 2026 compliant - using Claude Sonnet 4.5"
