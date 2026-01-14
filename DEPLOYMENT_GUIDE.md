# Deployment Guide - AI Therapy Platform
🏆 Breaking Barriers UK 2026 compliant

## Quick Deployment (15 minutes)

### Prerequisites
- AWS CLI configured with credentials
- Terraform installed
- Node.js and npm installed
- Python 3.9+ installed
- jq installed (for JSON parsing)

### Step 1: Run Integration Script (5 min)

```bash
# From project root
./integrate.sh
```

This will:
- ✅ Create Cognito frontend client (no secret)
- ✅ Update frontend configuration
- ✅ Enable real authentication
- ✅ Create environment files
- ✅ Install dependencies

### Step 2: Package Lambda Functions (2 min)

```bash
cd backend
python3 scripts/package_lambdas.py
```

This will:
- ✅ Package API handlers
- ✅ Package WebSocket handlers
- ✅ Include all dependencies
- ✅ Create deployment-ready zip files

Output: `backend/lambda_packages/*.zip`

### Step 3: Deploy Infrastructure (5 min)

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

This will deploy:
- ✅ Lambda functions (API + WebSocket handlers)
- ✅ API Gateway routes
- ✅ Cognito authorizer
- ✅ CloudWatch logs
- ✅ IAM permissions
- ✅ CORS configuration

### Step 4: Uncomment Frontend Code (2 min)

Search for these markers and uncomment the code:

```typescript
// REAL COGNITO CODE (COMMENTED OUT - BACKEND TEAM NEEDS TO FIX CLIENT SECRET ISSUE)
// REAL API INTEGRATION (COMMENTED OUT - WAITING FOR BACKEND)
// REAL WEBSOCKET CODE (COMMENTED OUT - BACKEND TEAM NEEDS TO SETUP WEBSOCKET AUTH)
```

**Files to update:**
- `ai-therapy-frontend/src/services/auth.ts`
- `ai-therapy-frontend/src/services/api.ts`
- `ai-therapy-frontend/src/services/websocket.ts`
- `ai-therapy-frontend/src/components/TherapistDashboard.tsx`
- `ai-therapy-frontend/src/components/AdminDashboard.tsx`

Or run the helper script:
```bash
cd backend
./scripts/enable_frontend_integration.sh
```

### Step 5: Start Frontend (1 min)

```bash
cd ai-therapy-frontend
npm run dev
```

Open http://localhost:3000

---

## Detailed Deployment Steps

### 1. Cognito Configuration

#### Create Frontend Client

The integration script automatically creates a Cognito client suitable for frontend use:

```bash
aws cognito-idp create-user-pool-client \
  --user-pool-id us-west-2_ASOPUuOOV \
  --client-name "ai-therapy-platform-frontend-client" \
  --no-generate-secret \
  --explicit-auth-flows "ALLOW_USER_SRP_AUTH" "ALLOW_REFRESH_TOKEN_AUTH" \
  --region us-west-2
```

**Key Features:**
- ✅ No client secret (secure for browsers)
- ✅ SRP authentication (Secure Remote Password)
- ✅ Refresh token support
- ✅ Custom attributes (role, language_preference)

#### Verify Configuration

```bash
aws cognito-idp describe-user-pool-client \
  --user-pool-id us-west-2_ASOPUuOOV \
  --client-id YOUR_CLIENT_ID \
  --region us-west-2
```

### 2. Lambda Packaging

#### Package Structure

```
lambda_packages/
├── api_handlers.zip
│   ├── lambda_functions/
│   │   └── api_handlers.py
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── session_service.py
│   │   ├── red_flag_service.py
│   │   └── notification_service.py
│   ├── repositories/
│   │   ├── user_repository.py
│   │   ├── session_repository.py
│   │   ├── red_flag_repository.py
│   │   └── notification_repository.py
│   └── [dependencies]
└── websocket_handlers.zip
    └── [similar structure]
```

#### Size Limits

- ✅ Unzipped: < 50MB (for inline editing)
- ✅ Zipped: < 10MB (for zipped inline editing)
- ✅ Total: < 250MB (Lambda limit)

If packages exceed limits:
1. Use Lambda Layers for dependencies
2. Remove unused dependencies
3. Use S3 for large files

### 3. Terraform Deployment

#### Initialize Terraform

```bash
cd terraform
terraform init
```

#### Review Changes

```bash
terraform plan
```

Expected resources:
- 2 Lambda functions
- 20+ API Gateway routes
- 1 Cognito authorizer
- 2 CloudWatch log groups
- Multiple IAM permissions

#### Apply Changes

```bash
terraform apply
```

Type `yes` to confirm.

#### Verify Deployment

```bash
# Check Lambda functions
aws lambda list-functions --region us-west-2 | grep ai-therapy

# Check API Gateway
aws apigatewayv2 get-apis --region us-west-2 | grep ai-therapy

# Check logs
aws logs describe-log-groups --region us-west-2 | grep ai-therapy
```

### 4. Frontend Configuration

#### Environment Variables

The integration script creates `.env.local`:

```bash
NEXT_PUBLIC_AWS_REGION=us-west-2
NEXT_PUBLIC_COGNITO_USER_POOL_ID=us-west-2_ASOPUuOOV
NEXT_PUBLIC_COGNITO_CLIENT_ID=YOUR_CLIENT_ID
NEXT_PUBLIC_API_URL=https://yqv4v90gj9.execute-api.us-west-2.amazonaws.com/dev
NEXT_PUBLIC_WEBSOCKET_URL=wss://yqv4v90gj9.execute-api.us-west-2.amazonaws.com/dev
```

#### AWS Configuration

File: `ai-therapy-frontend/src/config/aws-config.ts`

```typescript
export const awsConfig = {
  region: 'us-west-2',
  cognito: {
    userPoolId: 'us-west-2_ASOPUuOOV',
    userPoolWebClientId: 'YOUR_CLIENT_ID',  // Updated by script
  },
  apiGateway: {
    restApiUrl: 'https://yqv4v90gj9.execute-api.us-west-2.amazonaws.com/dev',
    websocketUrl: 'wss://yqv4v90gj9.execute-api.us-west-2.amazonaws.com/dev',
  },
};
```

#### Enable Real Authentication

File: `ai-therapy-frontend/src/services/auth.ts`

```typescript
const USE_MOCK_AUTH = false;  // Changed by script
```

### 5. Testing

#### Test Authentication

```bash
# Register user
curl -X POST https://yqv4v90gj9.execute-api.us-west-2.amazonaws.com/dev/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!","role":"client"}'

# Login
curl -X POST https://yqv4v90gj9.execute-api.us-west-2.amazonaws.com/dev/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}'
```

#### Test API Endpoints

```bash
# Get profile (requires JWT token)
curl -X GET https://yqv4v90gj9.execute-api.us-west-2.amazonaws.com/dev/auth/profile \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Create session
curl -X POST https://yqv4v90gj9.execute-api.us-west-2.amazonaws.com/dev/sessions \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"userId":"user123"}'
```

#### Test WebSocket

```javascript
const token = 'YOUR_JWT_TOKEN';
const ws = new WebSocket(`wss://yqv4v90gj9.execute-api.us-west-2.amazonaws.com/dev?token=${token}`);

ws.onopen = () => console.log('Connected');
ws.onmessage = (event) => console.log('Message:', event.data);
ws.onerror = (error) => console.error('Error:', error);
```

#### Test Frontend

1. **Register User**
   - Go to http://localhost:3000
   - Click "Sign Up"
   - Enter email and password
   - Verify email (check console for code)

2. **Login**
   - Enter credentials
   - Should see dashboard

3. **Test Client Session**
   - Click "Start Session"
   - Test audio controls
   - Verify WebSocket connection

4. **Test Therapist Dashboard**
   - Login as therapist
   - View red flags
   - Acknowledge/resolve flags
   - Check notifications

5. **Test Admin Dashboard**
   - Login as admin
   - View statistics
   - Check DynamoDB tables
   - Verify system health

---

## Troubleshooting

### Cognito Issues

**Error: "Client is configured with secret"**

Solution: Run integration script to create new client
```bash
./integrate.sh
```

**Error: "User pool does not exist"**

Solution: Verify user pool ID
```bash
aws cognito-idp describe-user-pool \
  --user-pool-id us-west-2_ASOPUuOOV \
  --region us-west-2
```

### Lambda Issues

**Error: "Function not found"**

Solution: Deploy with Terraform
```bash
cd terraform
terraform apply
```

**Error: "Package too large"**

Solution: Use Lambda Layers
```bash
# Create layer
cd backend
pip install -r requirements-lambda.txt -t python/
zip -r layer.zip python/

# Upload layer
aws lambda publish-layer-version \
  --layer-name ai-therapy-dependencies \
  --zip-file fileb://layer.zip \
  --compatible-runtimes python3.9 \
  --region us-west-2
```

### API Gateway Issues

**Error: "Missing Authentication Token"**

Solution: Check JWT token in Authorization header
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" ...
```

**Error: "CORS error"**

Solution: Verify CORS configuration in Terraform
```hcl
# Should have OPTIONS routes for all endpoints
resource "aws_apigatewayv2_route" "options_auth" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "OPTIONS /auth/{proxy+}"
  ...
}
```

### WebSocket Issues

**Error: "Connection failed"**

Solution: Check JWT token in URL
```javascript
const ws = new WebSocket(`wss://...?token=${token}`);
```

**Error: "Unauthorized"**

Solution: Verify token is valid
```bash
# Decode JWT token
echo "YOUR_TOKEN" | cut -d. -f2 | base64 -d | jq
```

### Frontend Issues

**Error: "Network error"**

Solution: Check API URL in configuration
```typescript
// Verify in aws-config.ts
apiGateway: {
  restApiUrl: 'https://yqv4v90gj9.execute-api.us-west-2.amazonaws.com/dev',
}
```

**Error: "Authentication failed"**

Solution: Verify USE_MOCK_AUTH is false
```typescript
// In auth.ts
const USE_MOCK_AUTH = false;
```

---

## Monitoring

### CloudWatch Logs

```bash
# View Lambda logs
aws logs tail /aws/lambda/ai-therapy-platform-dev-api-handlers --follow

# View API Gateway logs
aws logs tail /aws/apigateway/ai-therapy-platform-dev --follow
```

### Metrics

```bash
# Lambda invocations
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=ai-therapy-platform-dev-api-handlers \
  --start-time 2026-01-14T00:00:00Z \
  --end-time 2026-01-14T23:59:59Z \
  --period 3600 \
  --statistics Sum \
  --region us-west-2

# API Gateway requests
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApiGateway \
  --metric-name Count \
  --dimensions Name=ApiId,Value=yqv4v90gj9 \
  --start-time 2026-01-14T00:00:00Z \
  --end-time 2026-01-14T23:59:59Z \
  --period 3600 \
  --statistics Sum \
  --region us-west-2
```

### Alarms

Create CloudWatch alarms for:
- Lambda errors
- API Gateway 5xx errors
- High latency
- Throttling

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name ai-therapy-lambda-errors \
  --alarm-description "Alert on Lambda errors" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 300 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 1 \
  --region us-west-2
```

---

## Security Checklist

- [ ] Cognito client has no secret
- [ ] SRP authentication enabled
- [ ] JWT tokens expire after 1 hour
- [ ] Refresh tokens expire after 30 days
- [ ] API Gateway has Cognito authorizer
- [ ] CORS configured properly
- [ ] Lambda has minimal IAM permissions
- [ ] CloudWatch logs enabled
- [ ] Encryption at rest (DynamoDB)
- [ ] Encryption in transit (HTTPS/WSS)

---

## Performance Optimization

### Lambda

- Use provisioned concurrency for consistent performance
- Optimize cold start time
- Use Lambda Layers for dependencies
- Monitor memory usage

### API Gateway

- Enable caching for GET requests
- Use throttling to prevent abuse
- Monitor request latency

### DynamoDB

- Use GSI for efficient queries
- Enable auto-scaling
- Monitor read/write capacity

### Frontend

- Use code splitting
- Optimize bundle size
- Enable caching
- Use CDN for static assets

---

## Rollback Procedure

### Terraform Rollback

```bash
cd terraform
terraform plan -destroy
terraform destroy
```

### Frontend Rollback

```bash
cd ai-therapy-frontend

# Restore from backup
cp backup_TIMESTAMP/auth.ts src/services/
cp backup_TIMESTAMP/api.ts src/services/
cp backup_TIMESTAMP/websocket.ts src/services/

# Or revert to mock auth
# In src/services/auth.ts
const USE_MOCK_AUTH = true;
```

### Cognito Rollback

```bash
# Delete frontend client
aws cognito-idp delete-user-pool-client \
  --user-pool-id us-west-2_ASOPUuOOV \
  --client-id YOUR_CLIENT_ID \
  --region us-west-2
```

---

## 🏆 Breaking Barriers UK 2026 Compliance

All deployment follows hackathon constraints:

✅ **Region**: us-west-2 only
✅ **Rate Limiting**: < 1 RPS for Bedrock
✅ **Security**: No secrets in frontend
✅ **Serverless**: Lambda + API Gateway
✅ **Cost**: Optimized for free tier
✅ **Account Termination**: January 15, 2026 at 23:00

---

## Support

For issues:
1. Check CloudWatch logs
2. Review Terraform state
3. Verify configuration files
4. Test with curl/Postman
5. Check AWS console

For questions, see:
- `FRONTEND_BACKEND_INTEGRATION_GUIDE.md` - Detailed guide
- `INTEGRATION_QUICK_START.md` - Quick start
- `INTEGRATION_COMPLETE_SUMMARY.md` - Overview

---

**Created:** January 14, 2026
**Status:** Production Ready
**Time to Deploy:** ~15 minutes
