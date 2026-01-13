#!/bin/bash

# AI Therapy Platform - Terraform Destroy Script
# Breaking Barriers UK 2026 compliant cleanup

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(dirname "$SCRIPT_DIR")"

echo "🧹 AI Therapy Platform - Infrastructure Cleanup"
echo "🏆 Breaking Barriers UK 2026 compliant"
echo "=" * 50

# Check if we're in the right directory
if [ ! -f "$TERRAFORM_DIR/main.tf" ]; then
    echo "❌ Error: main.tf not found. Please run from terraform directory."
    exit 1
fi

cd "$TERRAFORM_DIR"

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

# Warning about data loss
echo ""
echo "⚠️  WARNING: This will destroy ALL infrastructure and data!"
echo "   - All DynamoDB tables and data will be deleted"
echo "   - All Lambda functions will be removed"
echo "   - All API Gateway endpoints will be deleted"
echo "   - All CloudWatch logs will be removed"
echo "   - All Cognito users will be deleted"
echo ""
echo "🏆 Breaking Barriers UK 2026: This is normal for hackathon cleanup"
echo "   Remember to save any important code to Git repositories!"
echo ""

# Double confirmation
read -p "🤔 Are you absolutely sure you want to destroy everything? (type 'yes' to confirm): " -r
echo ""

if [[ $REPLY == "yes" ]]; then
    echo "🧹 Planning destruction..."
    terraform plan -destroy -out=destroy-plan
    
    echo ""
    read -p "🔥 Final confirmation - destroy all resources? (y/N): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🔥 Destroying infrastructure..."
        terraform apply destroy-plan
        
        echo ""
        echo "🎉 Infrastructure destroyed successfully!"
        echo "🏆 Breaking Barriers UK 2026: Cleanup completed"
        
        # Clean up local files
        echo "🧹 Cleaning up local files..."
        rm -f terraform.tfstate.backup
        rm -f destroy-plan
        rm -f ../backend/.env.terraform
        
        echo "✅ Local cleanup completed"
        
    else
        echo "❌ Destruction cancelled"
        rm -f destroy-plan
        exit 1
    fi
else
    echo "❌ Destruction cancelled - 'yes' not entered"
    exit 1
fi

echo ""
echo "🏁 Cleanup script completed"