#!/bin/bash

# AI Therapy Platform - Terraform Deployment Script
# Breaking Barriers UK 2026 compliant deployment

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(dirname "$SCRIPT_DIR")"

echo "🚀 AI Therapy Platform - Terraform Deployment"
echo "🏆 Breaking Barriers UK 2026 compliant"
echo "=" * 50

# Check if we're in the right directory
if [ ! -f "$TERRAFORM_DIR/main.tf" ]; then
    echo "❌ Error: main.tf not found. Please run from terraform directory."
    exit 1
fi

cd "$TERRAFORM_DIR"

# Check if terraform.tfvars exists
if [ ! -f "terraform.tfvars" ]; then
    echo "⚠️  terraform.tfvars not found. Creating from example..."
    cp terraform.tfvars.example terraform.tfvars
    echo "✅ Please edit terraform.tfvars with your specific values"
fi

# Check AWS credentials
echo "🔍 Checking AWS credentials..."
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ AWS credentials not configured. Please set:"
    echo "   export AWS_ACCESS_KEY_ID=your_key"
    echo "   export AWS_SECRET_ACCESS_KEY=your_secret"
    echo "   export AWS_SESSION_TOKEN=your_token"
    echo "   export AWS_DEFAULT_REGION=us-west-2"
    exit 1
fi

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=$(aws configure get region || echo $AWS_DEFAULT_REGION)

echo "✅ AWS credentials valid"
echo "   Account ID: $ACCOUNT_ID"
echo "   Region: $REGION"

# Validate region for Breaking Barriers UK 2026
if [[ "$REGION" != "us-west-2" && "$REGION" != "us-east-1" ]]; then
    echo "⚠️  Adjusted for hackathon constraints: Only us-west-2 and us-east-1 regions are permitted"
    echo "   Current region: $REGION"
    echo "   Please set AWS_DEFAULT_REGION=us-west-2"
    exit 1
fi

# Initialize Terraform
echo "🔧 Initializing Terraform..."
terraform init

# Validate configuration
echo "🔍 Validating Terraform configuration..."
terraform validate

# Plan deployment
echo "📋 Planning deployment..."
terraform plan -out=tfplan

# Ask for confirmation
echo ""
read -p "🤔 Do you want to apply this plan? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Applying Terraform configuration..."
    terraform apply tfplan
    
    echo ""
    echo "🎉 Deployment completed successfully!"
    echo "🏆 Breaking Barriers UK 2026 compliant infrastructure deployed"
    
    # Display important outputs
    echo ""
    echo "📊 Important Information:"
    echo "========================"
    terraform output -json | jq -r '
        "Account ID: " + .account_id.value,
        "Region: " + .region.value,
        "Environment: " + .environment.value,
        "",
        "🔐 Cognito User Pool ID: " + .cognito_user_pool.value.id,
        "🔐 Cognito Client ID: " + .cognito_user_pool_client.value.id,
        "",
        "🌐 REST API Endpoint: " + .api_gateway_rest.value.invoke_url,
        "🔌 WebSocket Endpoint: " + .api_gateway_websocket.value.api_endpoint,
        "",
        "📊 DynamoDB Tables:",
        "  - Users: " + .dynamodb_tables.value.users_table.name,
        "  - Sessions: " + .dynamodb_tables.value.sessions_table.name,
        "  - Red Flags: " + .dynamodb_tables.value.redflags_table.name,
        "  - Notifications: " + .dynamodb_tables.value.notifications_table.name
    '
    
    # Save environment configuration
    echo ""
    echo "💾 Saving environment configuration..."
    terraform output -json environment_config | jq -r 'to_entries[] | "\(.key)=\(.value)"' > ../backend/.env.terraform
    echo "✅ Environment configuration saved to backend/.env.terraform"
    
    echo ""
    echo "⚠️  Remember: AWS accounts terminate at 23:00 on 15th January 2026"
    echo "   Save all work to Git repositories before this deadline!"
    
else
    echo "❌ Deployment cancelled"
    rm -f tfplan
    exit 1
fi

# Clean up plan file
rm -f tfplan

echo ""
echo "🏁 Deployment script completed"