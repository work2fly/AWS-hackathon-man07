# AI Therapy Platform - Terraform Infrastructure

🏆 Breaking Barriers UK 2026 compliant infrastructure as code

## Overview

This directory contains Terraform configuration for deploying the AI Therapy Platform infrastructure on AWS. The infrastructure includes:

- **DynamoDB Tables**: Users, Sessions, RedFlags, Notifications
- **AWS Cognito**: User authentication and management
- **API Gateway**: REST and WebSocket APIs
- **Lambda Functions**: Serverless compute
- **CloudWatch**: Monitoring and logging
- **KMS**: Encryption key management

## Prerequisites

1. **AWS CLI configured** with appropriate credentials
2. **Terraform >= 1.12** installed
3. **jq** installed for JSON processing
4. **Breaking Barriers UK 2026 constraints**:
   - Only `us-west-2` and `us-east-1` regions permitted
   - AWS accounts terminate at 23:00 on 15th January 2026

## Quick Start

### 1. Set up S3 Backend (Required)

The infrastructure uses S3 for Terraform state management with DynamoDB for state locking.

```bash
# Run the backend setup script
./scripts/setup-backend.sh
```

This creates:
- S3 bucket: `ai-therapy-platform-terraform-state`
- DynamoDB table: `ai-therapy-platform-terraform-locks`

### 2. Configure Variables

```bash
# Copy the example variables file
cp terraform.tfvars.example terraform.tfvars

# Edit with your specific values
nano terraform.tfvars
```

### 3. Deploy Infrastructure

```bash
# Deploy to development environment
./scripts/deploy.sh

# Or deploy to specific environment
./scripts/deploy.sh staging
```

## Manual Deployment Steps

If you prefer manual deployment:

```bash
# 1. Initialize Terraform with S3 backend
terraform init -backend-config=backend.hcl

# 2. Validate configuration
terraform validate

# 3. Plan deployment
terraform plan -out=tfplan

# 4. Apply changes
terraform apply tfplan
```

## Configuration Files

- **`main.tf`**: Main Terraform configuration and provider setup
- **`variables.tf`**: Input variables and validation
- **`dynamodb.tf`**: DynamoDB table definitions
- **`cognito.tf`**: AWS Cognito configuration
- **`api_gateway.tf`**: API Gateway setup
- **`iam.tf`**: IAM roles and policies
- **`cloudwatch.tf`**: Monitoring and logging
- **`outputs.tf`**: Output values
- **`backend.hcl`**: S3 backend configuration

## Environment Variables

After deployment, environment configuration is saved to `../backend/.env.terraform`:

```bash
# Load environment variables
source ../backend/.env.terraform
```

## State Management

### S3 Backend Structure
```
ai-therapy-platform-terraform-state/
├── dev/terraform.tfstate
├── staging/terraform.tfstate
└── prod/terraform.tfstate
```

### State Locking
DynamoDB table `ai-therapy-platform-terraform-locks` prevents concurrent modifications.

## Breaking Barriers UK 2026 Compliance

✅ **Permitted AWS Services**: All services used are on the approved list
✅ **Region Restrictions**: Only us-west-2 and us-east-1 regions
✅ **Bedrock Models**: Only permitted models configured
✅ **Security**: Encryption enabled for all resources
✅ **Cost Optimization**: Serverless and managed services prioritized

## Troubleshooting

### Backend Not Found
```bash
# Error: S3 bucket does not exist
./scripts/setup-backend.sh
```

### State Lock Issues
```bash
# Force unlock if needed (use carefully)
terraform force-unlock LOCK_ID
```

### Region Issues
```bash
# Ensure correct region is set
export AWS_DEFAULT_REGION=us-west-2
```

### Provider Version Issues
```bash
# Upgrade providers
terraform init -upgrade
```

## Cleanup

### Destroy Infrastructure
```bash
./scripts/destroy.sh
```

### Remove Backend (Optional)
```bash
# Delete S3 bucket contents
aws s3 rm s3://ai-therapy-platform-terraform-state --recursive

# Delete S3 bucket
aws s3api delete-bucket --bucket ai-therapy-platform-terraform-state

# Delete DynamoDB table
aws dynamodb delete-table --table-name ai-therapy-platform-terraform-locks
```

## Security Considerations

- **Encryption**: All data encrypted at rest and in transit
- **Access Control**: IAM roles with least privilege
- **State Security**: S3 bucket with versioning and encryption
- **Secrets**: No hardcoded secrets in configuration
- **Compliance**: GDPR-ready data handling (commented for hackathon)

## Monitoring

After deployment, monitor your infrastructure:

- **CloudWatch Dashboards**: Available in AWS Console
- **Logs**: Centralized in CloudWatch Logs
- **Metrics**: Custom metrics for business logic
- **Alerts**: Automated notifications for issues

## Support

For issues during Breaking Barriers UK 2026:

**Environment Leads**:
- **London**: Mevlit, Rama
- **Manchester**: Basheer Ahmed, Robert Bradley  
- **Dublin**: Shane Adams, Sherin Chandy, Eduarda Siqueira

---

🏆 **Breaking Barriers UK 2026** - Building the future of AI-powered therapy