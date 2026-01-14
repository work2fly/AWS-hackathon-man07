# Deployment Guide - AI Therapy Platform

🏆 Breaking Barriers UK 2026 compliant

## Quick Start Deployment

This guide shows how to deploy your AI therapy platform to AWS using the permitted services.

## Prerequisites

- AWS Account (Workshop Studio provided)
- AWS CLI configured
- Python 3.9+
- Node.js 18+ (for frontend)
- Git

## Architecture Overview

```
Frontend (Amplify/S3+CloudFront)
    ↓
API Gateway (REST API)
    ↓
Lambda Functions (Python 3.9)
    ├─ chat_handler
    ├─ session_analysis_handler
    ├─ user_management_handler
    └─ red_flag_handler
    ↓
AWS Services:
├─ Bedrock Agent (AI Chat)
├─ DynamoDB (Data Storage)
├─ Cognito (Authentication)
├─ SNS (Notifications)
└─ CloudWatch (Monitoring)
```

## Step 1: Set Up DynamoDB Tables

```bash
# Create Users table
aws dynamodb create-table \
    --table-name users \
    --attribute-definitions \
        AttributeName=userId,AttributeType=S \
        AttributeName=email,AttributeType=S \
    --key-schema \
        AttributeName=userId,KeyType=HASH \
    --global-secondary-indexes \
        IndexName=EmailIndex,KeySchema=[{AttributeName=email,KeyType=HASH}],Projection={ProjectionType=ALL},ProvisionedThroughput={ReadCapacityUnits=5,WriteCapacityUnits=5} \
    --provisioned-throughput \
        ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --region us-west-2

# Create Sessions table
aws dynamodb create-table \
    --table-name sessions \
    --attribute-definitions \
        AttributeName=sessionId,AttributeType=S \
        AttributeName=timestamp,AttributeType=S \
        AttributeName=clientId,AttributeType=S \
    --key-schema \
        AttributeName=sessionId,KeyType=HASH \
        AttributeName=timestamp,KeyType=RANGE \
    --global-secondary-indexes \
        IndexName=ClientIndex,KeySchema=[{AttributeName=clientId,KeyType=HASH},{AttributeName=timestamp,KeyType=RANGE}],Projection={ProjectionType=ALL},ProvisionedThroughput={ReadCapacityUnits=5,WriteCapacityUnits=5} \
    --provisioned-throughput \
        ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --region us-west-2

# Create RedFlags table
aws dynamodb create-table \
    --table-name redflags \
    --attribute-definitions \
        AttributeName=sessionId,AttributeType=S \
        AttributeName=flagId,AttributeType=S \
        AttributeName=severity,AttributeType=S \
        AttributeName=detectedAt,AttributeType=S \
    --key-schema \
        AttributeName=sessionId,KeyType=HASH \
        AttributeName=flagId,KeyType=RANGE \
    --global-secondary-indexes \
        IndexName=SeverityIndex,KeySchema=[{AttributeName=severity,KeyType=HASH},{AttributeName=detectedAt,KeyType=RANGE}],Projection={ProjectionType=ALL},ProvisionedThroughput={ReadCapacityUnits=5,WriteCapacityUnits=5} \
    --provisioned-throughput \
        ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --region us-west-2

# Enable encryption at rest (best practice)
aws dynamodb update-table \
    --table-name users \
    --sse-specification Enabled=true \
    --region us-west-2

aws dynamodb update-table \
    --table-name sessions \
    --sse-specification Enabled=true \
    --region us-west-2

aws dynamodb update-table \
    --table-name redflags \
    --sse-specification Enabled=true \
    --region us-west-2
```

## Step 2: Create Bedrock Agent

```bash
# Create IAM role for Bedrock Agent
aws iam create-role \
    --role-name BedrockAgentRole \
    --assume-role-policy-document '{
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "bedrock.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }]
    }' \
    --region us-west-2

# Attach necessary policies
aws iam attach-role-policy \
    --role-name BedrockAgentRole \
    --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess \
    --region us-west-2

# Create Bedrock Agent (using AWS Console or CLI)
# Note: Agent creation is easier through AWS Console
# Go to: AWS Console → Bedrock → Agents → Create Agent
# - Name: TherapyAgent
# - Model: Claude Sonnet 4.5
# - Instructions: [See AI_CHAT_INTEGRATION.md]
```

## Step 3: Package Lambda Functions

```bash
# Create deployment package
cd backend
mkdir -p lambda_package

# Install dependencies
pip install -r requirements.txt -t lambda_package/

# Copy source code
cp -r src/* lambda_package/

# Create ZIP file
cd lambda_package
zip -r ../lambda_deployment.zip .
cd ..

# Upload to S3 (for Lambda deployment)
aws s3 mb s3://therapy-platform-lambda-code --region us-west-2
aws s3 cp lambda_deployment.zip s3://therapy-platform-lambda-code/
```

## Step 4: Create Lambda Functions

```bash
# Create IAM role for Lambda
aws iam create-role \
    --role-name TherapyPlatformLambdaRole \
    --assume-role-policy-document '{
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "lambda.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }]
    }' \
    --region us-west-2

# Attach policies
aws iam attach-role-policy \
    --role-name TherapyPlatformLambdaRole \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

aws iam attach-role-policy \
    --role-name TherapyPlatformLambdaRole \
    --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess

aws iam attach-role-policy \
    --role-name TherapyPlatformLambdaRole \
    --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess

# Create Chat Handler Lambda
aws lambda create-function \
    --function-name therapy-chat-handler \
    --runtime python3.9 \
    --role arn:aws:iam::ACCOUNT_ID:role/TherapyPlatformLambdaRole \
    --handler api.chat_handler.chat_handler \
    --code S3Bucket=therapy-platform-lambda-code,S3Key=lambda_deployment.zip \
    --timeout 30 \
    --memory-size 512 \
    --environment Variables="{
        BEDROCK_AGENT_ID=your-agent-id,
        BEDROCK_AGENT_ALIAS_ID=your-alias-id,
        DYNAMODB_USERS_TABLE=users,
        DYNAMODB_SESSIONS_TABLE=sessions
    }" \
    --region us-west-2

# Create Session Analysis Lambda
aws lambda create-function \
    --function-name therapy-session-analysis \
    --runtime python3.9 \
    --role arn:aws:iam::ACCOUNT_ID:role/TherapyPlatformLambdaRole \
    --handler api.session_analysis.analyze_session_handler \
    --code S3Bucket=therapy-platform-lambda-code,S3Key=lambda_deployment.zip \
    --timeout 60 \
    --memory-size 512 \
    --environment Variables="{
        DYNAMODB_USERS_TABLE=users,
        DYNAMODB_SESSIONS_TABLE=sessions,
        DYNAMODB_REDFLAGS_TABLE=redflags
    }" \
    --region us-west-2

# Create End Session Lambda
aws lambda create-function \
    --function-name therapy-end-session \
    --runtime python3.9 \
    --role arn:aws:iam::ACCOUNT_ID:role/TherapyPlatformLambdaRole \
    --handler api.chat_handler.end_session_handler \
    --code S3Bucket=therapy-platform-lambda-code,S3Key=lambda_deployment.zip \
    --timeout 30 \
    --memory-size 256 \
    --environment Variables="{
        DYNAMODB_SESSIONS_TABLE=sessions
    }" \
    --region us-west-2
```

## Step 5: Create API Gateway

```bash
# Create REST API
aws apigateway create-rest-api \
    --name therapy-platform-api \
    --description "AI Therapy Platform API" \
    --region us-west-2

# Get API ID
API_ID=$(aws apigateway get-rest-apis --query "items[?name=='therapy-platform-api'].id" --output text --region us-west-2)

# Get root resource ID
ROOT_ID=$(aws apigateway get-resources --rest-api-id $API_ID --query "items[?path=='/'].id" --output text --region us-west-2)

# Create /chat resource
aws apigateway create-resource \
    --rest-api-id $API_ID \
    --parent-id $ROOT_ID \
    --path-part chat \
    --region us-west-2

CHAT_RESOURCE_ID=$(aws apigateway get-resources --rest-api-id $API_ID --query "items[?path=='/chat'].id" --output text --region us-west-2)

# Create POST method for /chat
aws apigateway put-method \
    --rest-api-id $API_ID \
    --resource-id $CHAT_RESOURCE_ID \
    --http-method POST \
    --authorization-type NONE \
    --region us-west-2

# Integrate with Lambda
aws apigateway put-integration \
    --rest-api-id $API_ID \
    --resource-id $CHAT_RESOURCE_ID \
    --http-method POST \
    --type AWS_PROXY \
    --integration-http-method POST \
    --uri arn:aws:apigateway:us-west-2:lambda:path/2015-03-31/functions/arn:aws:lambda:us-west-2:ACCOUNT_ID:function:therapy-chat-handler/invocations \
    --region us-west-2

# Grant API Gateway permission to invoke Lambda
aws lambda add-permission \
    --function-name therapy-chat-handler \
    --statement-id apigateway-invoke \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:execute-api:us-west-2:ACCOUNT_ID:$API_ID/*/*" \
    --region us-west-2

# Deploy API
aws apigateway create-deployment \
    --rest-api-id $API_ID \
    --stage-name prod \
    --region us-west-2

echo "API Endpoint: https://$API_ID.execute-api.us-west-2.amazonaws.com/prod"
```

## Step 6: Set Up Cognito (Authentication)

```bash
# Create User Pool
aws cognito-idp create-user-pool \
    --pool-name therapy-platform-users \
    --policies "PasswordPolicy={MinimumLength=8,RequireUppercase=true,RequireLowercase=true,RequireNumbers=true}" \
    --auto-verified-attributes email \
    --region us-west-2

USER_POOL_ID=$(aws cognito-idp list-user-pools --max-results 10 --query "UserPools[?Name=='therapy-platform-users'].Id" --output text --region us-west-2)

# Create User Pool Client
aws cognito-idp create-user-pool-client \
    --user-pool-id $USER_POOL_ID \
    --client-name therapy-platform-web \
    --generate-secret \
    --region us-west-2
```

## Step 7: Deploy Frontend

```bash
# Build frontend
cd frontend
npm install
npm run build

# Deploy to S3 + CloudFront (using Amplify is easier)
# Option 1: AWS Amplify (Recommended)
amplify init
amplify add hosting
amplify publish

# Option 2: S3 + CloudFront
aws s3 mb s3://therapy-platform-frontend --region us-west-2
aws s3 sync build/ s3://therapy-platform-frontend/
aws s3 website s3://therapy-platform-frontend/ --index-document index.html
```

## Step 8: Configure Monitoring

```bash
# Create CloudWatch Dashboard
aws cloudwatch put-dashboard \
    --dashboard-name therapy-platform \
    --dashboard-body file://cloudwatch-dashboard.json \
    --region us-west-2

# Create alarms for critical metrics
aws cloudwatch put-metric-alarm \
    --alarm-name high-red-flags \
    --alarm-description "Alert when red flags exceed threshold" \
    --metric-name RedFlagCount \
    --namespace TherapyPlatform \
    --statistic Sum \
    --period 300 \
    --threshold 5 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 1 \
    --region us-west-2
```

## Environment Variables Summary

Set these in your Lambda functions:

```bash
# Chat Handler
BEDROCK_AGENT_ID=your-agent-id
BEDROCK_AGENT_ALIAS_ID=your-alias-id
DYNAMODB_USERS_TABLE=users
DYNAMODB_SESSIONS_TABLE=sessions

# Session Analysis
DYNAMODB_USERS_TABLE=users
DYNAMODB_SESSIONS_TABLE=sessions
DYNAMODB_REDFLAGS_TABLE=redflags

# DO NOT SET (automatically provided by Lambda):
# AWS_REGION
# AWS_DEFAULT_REGION
# AWS_LAMBDA_FUNCTION_NAME
# etc.
```

## Testing Deployment

```bash
# Test API endpoint
curl -X POST https://YOUR_API_ID.execute-api.us-west-2.amazonaws.com/prod/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user",
    "message": "Hello",
    "create_session": true
  }'

# Expected response:
# {
#   "session_id": "session_test-user_1705234567",
#   "user_message": "Hello",
#   "ai_response": "Hello! How can I support you today?",
#   "timestamp": "2026-01-14T10:30:00Z"
# }
```

## Important Notes

### Region Constraints
- **CRITICAL**: Use only `us-west-2` (Oregon) for all services
- Use `us-east-1` only for global services like CloudFront

### Rate Limiting
- **CRITICAL**: Bedrock has 1 RPS limit - implement throttling
- Add delays between Bedrock calls if needed

### Account Termination
- **CRITICAL**: All AWS accounts terminate at 23:00 on 15th January 2026
- Save all code to Git before deadline
- Export any important data

### Cost Optimization
- Use DynamoDB on-demand pricing for variable workloads
- Set Lambda memory to minimum required (256-512 MB)
- Enable CloudWatch Logs retention (7 days max for hackathon)

## Troubleshooting

### Lambda Timeout
- Increase timeout to 30-60 seconds for Bedrock calls
- Check CloudWatch Logs for errors

### Bedrock Throttling
- Implement exponential backoff
- Add rate limiting in API Gateway

### DynamoDB Errors
- Check IAM permissions
- Verify table names in environment variables

## Next Steps

1. Configure Cognito authentication in frontend
2. Set up SNS for red flag notifications
3. Create CloudWatch dashboard for monitoring
4. Test end-to-end flow
5. Deploy to production

🏆 Breaking Barriers UK 2026 compliant - uses only permitted services in us-west-2 region.
