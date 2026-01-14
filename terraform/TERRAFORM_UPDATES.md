# Terraform Configuration Updates

🏆 Breaking Barriers UK 2026 compliant

## Summary

Updated Terraform infrastructure to include all new backend features implemented for the AI Therapy Platform, including clinical profiles, session analysis, sentiment tracking, API security, and red flag management.

## New Resources Added

### 1. Lambda Functions (terraform/lambda_functions.tf - NEW FILE)

Created dedicated Lambda function definitions for all new handlers:

- **chat_handler** - Handles AI chat interactions with Bedrock
  - Timeout: 60s (for Bedrock API calls)
  - Memory: 512MB
  - Environment: Sessions, Users, RedFlags, API Keys, Rate Limits tables

- **session_analysis** - Analyzes sessions and updates clinical profiles
  - Timeout: 60s
  - Memory: 512MB
  - Environment: Sessions, Users, RedFlags, Notifications tables

- **session_handlers** - Manages session lifecycle (create, get, end)
  - Timeout: 30s
  - Memory: 256MB
  - Environment: Sessions, Users, RedFlags, API Keys, Rate Limits tables

- **redflag_handlers** - Manages red flag queries and resolution
  - Timeout: 30s
  - Memory: 256MB
  - Environment: RedFlags, Sessions, Notifications tables

- **api_key_handlers** - Manages API key creation and revocation
  - Timeout: 30s
  - Memory: 256MB
  - Environment: API Keys, Users tables

- **notification_handlers** - Manages notification delivery and acknowledgment
  - Timeout: 30s
  - Memory: 256MB
  - Environment: Notifications, Users tables

### 2. API Gateway Routes (terraform/api_gateway.tf - UPDATED)

Added comprehensive API routes for all new endpoints:

#### Chat API
- `POST /chat/send` → chat_handler

#### Session API
- `POST /sessions/create` → session_handlers
- `GET /sessions/{sessionId}` → session_handlers
- `POST /sessions/{sessionId}/end` → session_handlers
- `GET /sessions/{sessionId}/analysis` → session_analysis
- `GET /sessions/{sessionId}/sentiment-history` → session_analysis

#### Red Flag API
- `GET /redflags/session/{sessionId}` → redflag_handlers
- `GET /redflags/severity/{severity}` → redflag_handlers

#### API Key Management
- `POST /api-keys/create` → api_key_handlers
- `DELETE /api-keys/{keyId}` → api_key_handlers

#### Notifications
- `GET /notifications` → notification_handlers
- `POST /notifications/{notificationId}/acknowledge` → notification_handlers

### 3. DynamoDB Tables (Already Existed)

Confirmed existing tables support all new features:
- ✅ `api_keys` - API key storage with UserIndex GSI
- ✅ `rate_limits` - Rate limiting with TTL
- ✅ `websocket_connections` - WebSocket connection tracking
- ✅ `users` - User profiles with clinical data
- ✅ `sessions` - Session metadata with sentiment scores
- ✅ `redflags` - Red flag tracking with SeverityIndex GSI
- ✅ `notifications` - Notification delivery with PriorityIndex GSI

### 4. Outputs (terraform/outputs.tf - UPDATED)

Added comprehensive outputs for:

#### Lambda Functions
- All 11 Lambda function names and ARNs
- Includes: auth, chat, session analysis, session handlers, red flags, API keys, notifications, cognito triggers, websocket handlers

#### DynamoDB Tables
- All 7 table names and ARNs
- Added: api_keys, rate_limits, websocket_connections

#### Environment Configuration
- Updated with all new table names
- Ready for application configuration

## Existing Resources (No Changes Needed)

### IAM Roles & Policies
- ✅ Lambda execution role already has permissions for:
  - DynamoDB (all tables including new ones)
  - Bedrock (with permitted model restrictions)
  - Cognito (user management)
  - KMS (encryption)
  - CloudWatch (logging)
  - X-Ray (tracing)

### Security Features
- ✅ KMS encryption enabled for all DynamoDB tables
- ✅ Point-in-time recovery enabled
- ✅ SSL/TLS enforced for data in transit
- ✅ Advanced security mode for Cognito

### Monitoring
- ✅ CloudWatch log groups configured
- ✅ X-Ray tracing enabled
- ✅ API Gateway access logging configured

## Deployment Instructions

### 1. Package Lambda Functions

Create deployment packages for each Lambda function:

```bash
cd backend/scripts
python package_lambdas.py
```

This will create ZIP files:
- `chat_handler.zip`
- `session_analysis.zip`
- `session_handlers.zip`
- `redflag_handlers.zip`
- `api_key_handlers.zip`
- `notification_handlers.zip`
- `auth_handlers.zip`
- `cognito_triggers.zip`
- `websocket_handlers.zip`

### 2. Initialize Terraform

```bash
cd terraform
terraform init -backend-config=backend.hcl
```

### 3. Review Changes

```bash
terraform plan
```

Expected changes:
- 6 new Lambda functions
- 20+ new API Gateway resources/methods/integrations
- Updated outputs

### 4. Apply Changes

```bash
terraform apply
```

### 5. Verify Deployment

```bash
# Get API endpoint
terraform output api_gateway_rest

# Get Lambda functions
terraform output lambda_functions

# Get environment configuration
terraform output environment_config
```

## Breaking Barriers UK 2026 Compliance

✅ **Region**: All resources deployed to `us-west-2`
✅ **Bedrock Models**: Only permitted models configured
✅ **Rate Limiting**: Designed to stay below 1 RPS for Bedrock
✅ **Lambda Variables**: No reserved environment variables set
✅ **Encryption**: KMS encryption enabled for all data at rest
✅ **Security**: SSL/TLS enforced for data in transit
✅ **Services**: Only permitted AWS services used
✅ **Monitoring**: CloudWatch logging and X-Ray tracing enabled

## Environment Variables

Lambda functions automatically receive these from Terraform:

### Common Variables
- `COGNITO_USER_POOL_ID` - Cognito user pool ID
- `BEDROCK_MODEL_ID` - Permitted Bedrock model

### Table Names
- `USERS_TABLE_NAME`
- `SESSIONS_TABLE_NAME`
- `REDFLAGS_TABLE_NAME`
- `NOTIFICATIONS_TABLE_NAME`
- `API_KEYS_TABLE_NAME`
- `RATE_LIMITS_TABLE_NAME`
- `WEBSOCKET_CONNECTIONS_TABLE_NAME`

### API Endpoints
- `WEBSOCKET_API_ENDPOINT` - WebSocket API endpoint

**Note**: AWS Lambda automatically provides `AWS_REGION` and `AWS_DEFAULT_REGION` - these are NOT set in Terraform to avoid `InvalidParameterValueException`.

## Cost Optimization

- **DynamoDB**: PAY_PER_REQUEST billing mode (no idle costs)
- **Lambda**: Only charged for execution time
- **API Gateway**: Pay per request
- **CloudWatch**: 7-day log retention (reduced for hackathon)
- **KMS**: Single key for all encryption needs

## Next Steps

1. ✅ Package Lambda functions
2. ✅ Run `terraform plan` to review changes
3. ✅ Run `terraform apply` to deploy
4. ✅ Test API endpoints
5. ✅ Monitor CloudWatch logs
6. ✅ Save all work to Git before 23:00 on 15th January 2026

## Files Modified

- ✅ `terraform/lambda_functions.tf` - NEW (6 Lambda functions)
- ✅ `terraform/api_gateway.tf` - UPDATED (20+ new routes)
- ✅ `terraform/outputs.tf` - UPDATED (Lambda and table outputs)
- ✅ `terraform/dynamodb.tf` - NO CHANGES (already had all tables)
- ✅ `terraform/iam.tf` - NO CHANGES (permissions already sufficient)
- ✅ `terraform/cognito.tf` - NO CHANGES (already configured)
- ✅ `terraform/main.tf` - NO CHANGES (base configuration)
- ✅ `terraform/variables.tf` - NO CHANGES (all variables present)

## Support

For deployment issues, contact Environment Leads:
- **London**: Mevlit (mevlit@), Rama (ramaknat@)
- **Manchester**: Basheer Ahmed (basheerz@), Robert Bradley (rbradaws@)
- **Dublin**: Shane Adams (shaadas@), Sherin Chandy (chandys@), Eduarda Siqueira (edds@)
