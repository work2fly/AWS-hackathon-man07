# AI Therapy Platform - Terraform Deployment Guide

🏆 Breaking Barriers UK 2026 compliant deployment instructions

## Prerequisites

1. **AWS Credentials**: Configure AWS credentials for `us-west-2` region
   ```bash
   aws configure
   # or
   export AWS_ACCESS_KEY_ID=your_access_key
   export AWS_SECRET_ACCESS_KEY=your_secret_key
   export AWS_DEFAULT_REGION=us-west-2
   ```

2. **Terraform Variables**: Copy and configure the variables file
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars with your specific values
   ```

## Deployment Steps

### 1. Build Lambda Packages
```bash
# Run from project root
./terraform/scripts/build-lambda-packages.sh
```

This creates:
- `cognito_triggers.zip` - Cognito lifecycle triggers
- `auth_handlers.zip` - Authentication API handlers

### 2. Initialize Terraform
```bash
cd terraform
terraform init
```

### 3. Plan Deployment
```bash
terraform plan
```

Review the plan to ensure all resources are configured correctly.

### 4. Deploy Infrastructure
```bash
terraform apply
```

Type `yes` when prompted to confirm deployment.

## Post-Deployment

### 1. Verify API Gateway
```bash
# Get API Gateway URL from outputs
terraform output api_gateway_url

# Test health endpoint
curl https://your-api-id.execute-api.us-west-2.amazonaws.com/dev/health
```

### 2. Test Authentication
```bash
# Register a test user
curl -X POST https://your-api-id.execute-api.us-west-2.amazonaws.com/dev/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "[test_email]",
    "password": "TestPass123!",
    "role": "client"
  }'
```

### 3. Verify Cognito User Pool
- Check AWS Console → Cognito → User Pools
- Verify user groups (clients, therapists, admins) are created
- Test MFA configuration

## Troubleshooting

### Lambda Package Issues
If Lambda functions fail to deploy:
```bash
# Rebuild packages
./terraform/scripts/build-lambda-packages.sh

# Redeploy
terraform apply
```

### Reserved Environment Variable Error
If you see an error about `AWS_REGION` being a reserved key:
- This has been fixed in the current configuration
- AWS Lambda automatically provides `AWS_DEFAULT_REGION` environment variable
- No manual region configuration needed in Lambda environment variables

### Cognito Trigger Issues
Check CloudWatch Logs:
- `/aws/lambda/ai-therapy-platform-dev-cognito-triggers`
- `/aws/lambda/ai-therapy-platform-dev-auth-handlers`

### API Gateway Issues
- Verify Lambda permissions in AWS Console
- Check API Gateway deployment status
- Review CloudWatch API Gateway logs

## Security Notes

🔒 **Breaking Barriers UK 2026 Security Compliance**:
- All data encrypted at rest and in transit
- MFA enabled for user accounts
- JWT tokens with 1-hour expiration
- Role-based access control (RBAC)
- Audit logging for authentication events
- No PII stored in logs or error messages

## Resource Cleanup

To destroy all resources:
```bash
terraform destroy
```

⚠️ **Important**: Save all code to Git before account termination at 23:00 on 15th January 2026!

## Architecture Overview

The deployment creates:
- **Cognito User Pool**: User authentication and management
- **Lambda Functions**: Authentication handlers and triggers
- **API Gateway**: REST API endpoints
- **DynamoDB**: User data storage
- **CloudWatch**: Monitoring and logging
- **IAM Roles**: Secure service permissions

All services are deployed in `us-west-2` region as per hackathon requirements.