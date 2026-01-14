# AI Therapy Platform - Deployment Checklist

🏆 Breaking Barriers UK 2026 compliant

## Pre-Deployment Checklist

### 1. Environment Setup
- [ ] AWS CLI configured with credentials
- [ ] Terraform installed (v1.12+)
- [ ] Python 3.11 installed
- [ ] Git repository up to date
- [ ] Working in `us-west-2` region

### 2. Code Preparation
- [ ] All Python dependencies listed in `backend/requirements.txt`
- [ ] Lambda-specific dependencies in `backend/requirements-lambda.txt`
- [ ] All code committed to Git (accounts terminate 23:00 on 15th January 2026)

### 3. Lambda Package Creation

```bash
cd backend/scripts
python package_lambdas.py
```

Expected output:
- [ ] `chat_handler.zip` created
- [ ] `session_analysis.zip` created
- [ ] `session_handlers.zip` created
- [ ] `redflag_handlers.zip` created
- [ ] `api_key_handlers.zip` created
- [ ] `notification_handlers.zip` created
- [ ] `auth_handlers.zip` created
- [ ] `cognito_triggers.zip` created
- [ ] `websocket_handlers.zip` created

### 4. Terraform Configuration

```bash
cd terraform
```

- [ ] Review `terraform.tfvars.example`
- [ ] Create `terraform.tfvars` with your values
- [ ] Review `backend.hcl` for S3 backend configuration

### 5. Terraform Initialization

```bash
terraform init -backend-config=backend.hcl
```

Expected output:
- [ ] Backend initialized successfully
- [ ] Providers downloaded
- [ ] No errors

## Deployment Steps

### Step 1: Plan Infrastructure

```bash
terraform plan -out=tfplan
```

Review the plan:
- [ ] 11 Lambda functions to be created
- [ ] 7 DynamoDB tables to be created
- [ ] API Gateway REST API to be created
- [ ] API Gateway WebSocket API to be created
- [ ] IAM roles and policies to be created
- [ ] Cognito User Pool to be created
- [ ] KMS key to be created
- [ ] CloudWatch log groups to be created
- [ ] No unexpected deletions or modifications

Expected resource count: ~80-100 resources

### Step 2: Apply Infrastructure

```bash
terraform apply tfplan
```

Monitor the deployment:
- [ ] DynamoDB tables created (7 tables)
- [ ] Lambda functions deployed (11 functions)
- [ ] API Gateway configured
- [ ] IAM roles created
- [ ] Cognito User Pool created
- [ ] No errors during deployment

Deployment time: ~5-10 minutes

### Step 3: Verify Deployment

```bash
# Get outputs
terraform output

# Test API endpoint
terraform output api_gateway_rest

# Get Lambda functions
terraform output lambda_functions

# Get DynamoDB tables
terraform output dynamodb_tables
```

Verify:
- [ ] API Gateway endpoint URL received
- [ ] All Lambda functions listed
- [ ] All DynamoDB tables listed
- [ ] Cognito User Pool ID received

### Step 4: Test Health Check

```bash
# Get API endpoint
API_ENDPOINT=$(terraform output -raw api_gateway_rest | jq -r '.invoke_url')

# Test health check
curl $API_ENDPOINT/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "ai-therapy-platform",
  "timestamp": "..."
}
```

- [ ] Health check returns 200 OK
- [ ] Response contains expected fields

### Step 5: Test Authentication

```bash
# Register a test user
curl -X POST $API_ENDPOINT/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!",
    "name": "Test User",
    "role": "client"
  }'
```

- [ ] User registration successful
- [ ] Verification email sent (check Cognito console)

### Step 6: Verify DynamoDB Tables

```bash
# List tables
aws dynamodb list-tables --region us-west-2

# Check users table
aws dynamodb describe-table \
  --table-name ai-therapy-platform-dev-users \
  --region us-west-2
```

Verify:
- [ ] All 7 tables exist
- [ ] Encryption enabled
- [ ] GSIs configured correctly
- [ ] TTL enabled where needed

### Step 7: Verify Lambda Functions

```bash
# List functions
aws lambda list-functions --region us-west-2

# Check chat handler
aws lambda get-function \
  --function-name ai-therapy-platform-dev-chat-handler \
  --region us-west-2
```

Verify:
- [ ] All 11 functions deployed
- [ ] Environment variables set correctly
- [ ] IAM role attached
- [ ] Memory and timeout configured

### Step 8: Check CloudWatch Logs

```bash
# List log groups
aws logs describe-log-groups \
  --log-group-name-prefix /aws/lambda/ai-therapy-platform \
  --region us-west-2
```

Verify:
- [ ] Log groups created for all Lambda functions
- [ ] Retention period set to 7 days
- [ ] No errors in logs

## Post-Deployment Verification

### API Endpoints to Test

1. **Health Check**
   ```bash
   curl $API_ENDPOINT/health
   ```
   - [ ] Returns 200 OK

2. **Authentication**
   ```bash
   # Register
   curl -X POST $API_ENDPOINT/auth/register -d '{...}'
   
   # Login
   curl -X POST $API_ENDPOINT/auth/login -d '{...}'
   ```
   - [ ] Registration works
   - [ ] Login works
   - [ ] JWT tokens returned

3. **Session Management**
   ```bash
   # Create session
   curl -X POST $API_ENDPOINT/sessions/create \
     -H "Authorization: Bearer $TOKEN" \
     -d '{...}'
   ```
   - [ ] Session created
   - [ ] Session ID returned

4. **Chat**
   ```bash
   # Send message
   curl -X POST $API_ENDPOINT/chat/send \
     -H "Authorization: Bearer $TOKEN" \
     -d '{...}'
   ```
   - [ ] Message sent
   - [ ] AI response received

### Monitoring Setup

1. **CloudWatch Dashboards**
   ```bash
   cd backend/monitoring
   aws cloudwatch put-dashboard \
     --dashboard-name ai-therapy-platform \
     --dashboard-body file://dashboard_config.json \
     --region us-west-2
   ```
   - [ ] Dashboard created
   - [ ] Metrics visible

2. **CloudWatch Alarms**
   - [ ] Lambda error rate alarms
   - [ ] DynamoDB throttling alarms
   - [ ] API Gateway 5xx error alarms

3. **X-Ray Tracing**
   - [ ] X-Ray enabled for Lambda functions
   - [ ] Traces visible in X-Ray console

## Security Verification

### 1. Encryption
- [ ] DynamoDB tables encrypted with KMS
- [ ] S3 buckets encrypted (if any)
- [ ] API Gateway uses HTTPS only
- [ ] Lambda environment variables encrypted

### 2. IAM Permissions
- [ ] Lambda execution role has minimum required permissions
- [ ] No wildcard permissions in policies
- [ ] Cognito User Pool has proper password policy
- [ ] MFA enabled for admin users

### 3. Network Security
- [ ] API Gateway has throttling enabled
- [ ] CORS configured correctly
- [ ] Security headers present in responses

### 4. Bedrock Compliance
- [ ] Only permitted models configured
- [ ] Rate limiting in place (< 1 RPS)
- [ ] Error handling for throttling

## Troubleshooting

### Common Issues

1. **Lambda Function Fails**
   - Check CloudWatch logs
   - Verify environment variables
   - Check IAM permissions
   - Verify package size (< 50MB unzipped)

2. **DynamoDB Access Denied**
   - Check IAM role permissions
   - Verify table names in environment variables
   - Check KMS key permissions

3. **API Gateway 403 Errors**
   - Check Cognito authentication
   - Verify API key (if using)
   - Check CORS configuration

4. **Bedrock Throttling**
   - Implement exponential backoff
   - Reduce request rate
   - Check rate limiting configuration

### Rollback Procedure

If deployment fails:

```bash
# Destroy infrastructure
terraform destroy

# Or rollback to previous state
terraform apply -target=<resource>
```

## Cost Monitoring

### Expected Costs (Hackathon)

- **DynamoDB**: ~$0 (free tier, PAY_PER_REQUEST)
- **Lambda**: ~$0 (free tier, 1M requests/month)
- **API Gateway**: ~$0 (free tier, 1M requests/month)
- **Bedrock**: ~$0.003 per 1K input tokens, ~$0.015 per 1K output tokens
- **CloudWatch**: ~$0 (free tier, 5GB logs/month)
- **KMS**: ~$1/month per key

Total estimated cost: < $10 for hackathon duration

### Cost Optimization

- [ ] Use PAY_PER_REQUEST for DynamoDB
- [ ] Set appropriate Lambda memory sizes
- [ ] Use 7-day log retention
- [ ] Delete unused resources after hackathon

## Final Checklist

- [ ] All infrastructure deployed successfully
- [ ] All API endpoints tested and working
- [ ] CloudWatch monitoring configured
- [ ] Security verified
- [ ] Documentation updated
- [ ] Code committed to Git
- [ ] Team members have access
- [ ] Emergency contacts noted

## Emergency Contacts

**Environment Leads:**
- **London**: Mevlit (mevlit@), Rama (ramaknat@)
- **Manchester**: Basheer Ahmed (basheerz@), Robert Bradley (rbradaws@)
- **Dublin**: Shane Adams (shaadas@), Sherin Chandy (chandys@), Eduarda Siqueira (edds@)

## Important Reminders

⚠️ **CRITICAL**: AWS accounts terminate at 23:00 on 15th January 2026
- Save all work to Git before this time
- Export any important data
- Document all configurations

🏆 **Breaking Barriers UK 2026**: Follow all hackathon constraints
- Only use permitted services
- Stay in us-west-2 region
- Keep Bedrock requests < 1 RPS
- No reserved Lambda environment variables

## Next Steps After Deployment

1. [ ] Frontend integration
2. [ ] End-to-end testing
3. [ ] Performance optimization
4. [ ] User acceptance testing
5. [ ] Documentation review
6. [ ] Demo preparation

---

**Deployment Date**: _________________
**Deployed By**: _________________
**Environment**: _________________
**Git Commit**: _________________
