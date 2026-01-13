#!/bin/bash
# Setup S3 backend for Terraform state management
# 🏆 Breaking Barriers UK 2026 compliant

set -e

# Configuration
BUCKET_NAME="ai-therapy-platform-terraform-state"
DYNAMODB_TABLE="ai-therapy-platform-terraform-locks"
REGION="us-west-2"

echo "🏆 Breaking Barriers UK 2026 - Setting up Terraform S3 Backend"
echo "=================================================="

# Check if AWS CLI is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ AWS CLI is not configured. Please run 'aws configure' first."
    exit 1
fi

# Get current AWS account ID and region
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
CURRENT_REGION=$(aws configure get region || echo "us-west-2")

echo "📋 Configuration:"
echo "   Account ID: $ACCOUNT_ID"
echo "   Region: $REGION"
echo "   S3 Bucket: $BUCKET_NAME"
echo "   DynamoDB Table: $DYNAMODB_TABLE"
echo ""

# Create S3 bucket for Terraform state
echo "🪣 Creating S3 bucket for Terraform state..."
if aws s3api head-bucket --bucket "$BUCKET_NAME" 2>/dev/null; then
    echo "   ✅ S3 bucket $BUCKET_NAME already exists"
else
    if [ "$REGION" = "us-east-1" ]; then
        # us-east-1 doesn't need LocationConstraint
        aws s3api create-bucket --bucket "$BUCKET_NAME" --region "$REGION"
    else
        aws s3api create-bucket \
            --bucket "$BUCKET_NAME" \
            --region "$REGION" \
            --create-bucket-configuration LocationConstraint="$REGION"
    fi
    echo "   ✅ Created S3 bucket $BUCKET_NAME"
fi

# Enable versioning on the S3 bucket
echo "🔄 Enabling versioning on S3 bucket..."
aws s3api put-bucket-versioning \
    --bucket "$BUCKET_NAME" \
    --versioning-configuration Status=Enabled
echo "   ✅ Versioning enabled"

# Enable server-side encryption
echo "🔐 Enabling server-side encryption on S3 bucket..."
aws s3api put-bucket-encryption \
    --bucket "$BUCKET_NAME" \
    --server-side-encryption-configuration '{
        "Rules": [
            {
                "ApplyServerSideEncryptionByDefault": {
                    "SSEAlgorithm": "AES256"
                },
                "BucketKeyEnabled": true
            }
        ]
    }'
echo "   ✅ Server-side encryption enabled"

# Block public access
echo "🚫 Blocking public access to S3 bucket..."
aws s3api put-public-access-block \
    --bucket "$BUCKET_NAME" \
    --public-access-block-configuration \
        BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
echo "   ✅ Public access blocked"

# Create DynamoDB table for state locking
echo "🔒 Creating DynamoDB table for state locking..."
if aws dynamodb describe-table --table-name "$DYNAMODB_TABLE" --region "$REGION" > /dev/null 2>&1; then
    echo "   ✅ DynamoDB table $DYNAMODB_TABLE already exists"
else
    aws dynamodb create-table \
        --table-name "$DYNAMODB_TABLE" \
        --attribute-definitions AttributeName=LockID,AttributeType=S \
        --key-schema AttributeName=LockID,KeyType=HASH \
        --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
        --region "$REGION" \
        --tags Key=Project,Value=ai-therapy-platform \
               Key=Environment,Value=dev \
               Key=Team,Value=backend \
               Key=Event,Value=breaking-barriers-uk-2026 \
               Key=ManagedBy,Value=script
    
    echo "   ⏳ Waiting for DynamoDB table to be active..."
    aws dynamodb wait table-exists --table-name "$DYNAMODB_TABLE" --region "$REGION"
    echo "   ✅ Created DynamoDB table $DYNAMODB_TABLE"
fi

echo ""
echo "🎉 Terraform S3 backend setup complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Run 'terraform init' to initialize the backend"
echo "   2. If you have existing local state, run 'terraform init -migrate-state'"
echo "   3. Proceed with your Terraform operations"
echo ""
echo "🏆 Breaking Barriers UK 2026 compliant infrastructure ready!"