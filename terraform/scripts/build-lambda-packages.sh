#!/bin/bash

# Build Lambda deployment packages for AI Therapy Platform
# Breaking Barriers UK 2026 compliant

set -e

echo "🏆 Breaking Barriers UK 2026 compliant - Building Lambda packages..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$(dirname "$TERRAFORM_DIR")/backend"
BUILD_DIR="$TERRAFORM_DIR/lambda-builds"

# Clean and create build directory
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

echo "Building Cognito triggers Lambda package..."

# Create cognito_triggers package
COGNITO_BUILD_DIR="$BUILD_DIR/cognito_triggers"
mkdir -p "$COGNITO_BUILD_DIR"

# Copy the main Lambda function
cp "$BACKEND_DIR/src/lambda_functions/cognito_triggers.py" "$COGNITO_BUILD_DIR/"

# Copy required modules
mkdir -p "$COGNITO_BUILD_DIR/utils"
cp "$BACKEND_DIR/src/utils/logger.py" "$COGNITO_BUILD_DIR/utils/"
cp "$BACKEND_DIR/src/utils/validation.py" "$COGNITO_BUILD_DIR/utils/"
cp "$BACKEND_DIR/src/utils/__init__.py" "$COGNITO_BUILD_DIR/utils/" 2>/dev/null || touch "$COGNITO_BUILD_DIR/utils/__init__.py"

mkdir -p "$COGNITO_BUILD_DIR/data"
cp "$BACKEND_DIR/src/data/user_repository.py" "$COGNITO_BUILD_DIR/data/"
cp "$BACKEND_DIR/src/data/base.py" "$COGNITO_BUILD_DIR/data/"
cp "$BACKEND_DIR/src/data/__init__.py" "$COGNITO_BUILD_DIR/data/" 2>/dev/null || touch "$COGNITO_BUILD_DIR/data/__init__.py"

mkdir -p "$COGNITO_BUILD_DIR/models"
cp "$BACKEND_DIR/src/models/user.py" "$COGNITO_BUILD_DIR/models/"
cp "$BACKEND_DIR/src/models/__init__.py" "$COGNITO_BUILD_DIR/models/" 2>/dev/null || touch "$COGNITO_BUILD_DIR/models/__init__.py"

mkdir -p "$COGNITO_BUILD_DIR/config"
cp "$BACKEND_DIR/src/config/aws_config.py" "$COGNITO_BUILD_DIR/config/"
cp "$BACKEND_DIR/src/config/__init__.py" "$COGNITO_BUILD_DIR/config/" 2>/dev/null || touch "$COGNITO_BUILD_DIR/config/__init__.py"

# Create ZIP package for cognito_triggers
cd "$COGNITO_BUILD_DIR"
zip -r "$TERRAFORM_DIR/cognito_triggers.zip" . -x "*.pyc" "*__pycache__*"

echo "Building auth handlers Lambda package..."

# Create auth_handlers package
AUTH_BUILD_DIR="$BUILD_DIR/auth_handlers"
mkdir -p "$AUTH_BUILD_DIR"

# Copy the main Lambda function
cp "$BACKEND_DIR/src/lambda_functions/auth_handlers.py" "$AUTH_BUILD_DIR/"

# Copy required modules (same as cognito_triggers plus services)
mkdir -p "$AUTH_BUILD_DIR/utils"
cp "$BACKEND_DIR/src/utils/logger.py" "$AUTH_BUILD_DIR/utils/"
cp "$BACKEND_DIR/src/utils/validation.py" "$AUTH_BUILD_DIR/utils/"
cp "$BACKEND_DIR/src/utils/__init__.py" "$AUTH_BUILD_DIR/utils/" 2>/dev/null || touch "$AUTH_BUILD_DIR/utils/__init__.py"

mkdir -p "$AUTH_BUILD_DIR/data"
cp "$BACKEND_DIR/src/data/user_repository.py" "$AUTH_BUILD_DIR/data/"
cp "$BACKEND_DIR/src/data/base.py" "$AUTH_BUILD_DIR/data/"
cp "$BACKEND_DIR/src/data/__init__.py" "$AUTH_BUILD_DIR/data/" 2>/dev/null || touch "$AUTH_BUILD_DIR/data/__init__.py"

mkdir -p "$AUTH_BUILD_DIR/models"
cp "$BACKEND_DIR/src/models/user.py" "$AUTH_BUILD_DIR/models/"
cp "$BACKEND_DIR/src/models/__init__.py" "$AUTH_BUILD_DIR/models/" 2>/dev/null || touch "$AUTH_BUILD_DIR/models/__init__.py"

mkdir -p "$AUTH_BUILD_DIR/config"
cp "$BACKEND_DIR/src/config/aws_config.py" "$AUTH_BUILD_DIR/config/"
cp "$BACKEND_DIR/src/config/__init__.py" "$AUTH_BUILD_DIR/config/" 2>/dev/null || touch "$AUTH_BUILD_DIR/config/__init__.py"

mkdir -p "$AUTH_BUILD_DIR/services"
cp "$BACKEND_DIR/src/services/cognito_service.py" "$AUTH_BUILD_DIR/services/"
cp "$BACKEND_DIR/src/services/__init__.py" "$AUTH_BUILD_DIR/services/" 2>/dev/null || touch "$AUTH_BUILD_DIR/services/__init__.py"

# Create ZIP package for auth_handlers
cd "$AUTH_BUILD_DIR"
zip -r "$TERRAFORM_DIR/auth_handlers.zip" . -x "*.pyc" "*__pycache__*"

# Clean up build directory
cd "$TERRAFORM_DIR"
rm -rf "$BUILD_DIR"

echo "✅ Lambda packages built successfully:"
echo "  - cognito_triggers.zip ($(du -h cognito_triggers.zip | cut -f1))"
echo "  - auth_handlers.zip ($(du -h auth_handlers.zip | cut -f1))"
echo ""
echo "Ready for terraform apply!"