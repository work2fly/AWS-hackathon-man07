# AWS Infrastructure Changes - Manual Updates
🏆 Breaking Barriers UK 2026 compliant

## ⚠️ IMPORTANT: These changes were made manually via AWS CLI and are NOT in Terraform/IaC

If you need to recreate the infrastructure, you must apply these changes manually after Terraform deployment.

---

## 1. API Gateway WebSocket - Authorization Changes

### Change: Removed AWS_IAM authorization from $connect route

**Command:**
```bash
aws apigatewayv2 update-route \
  --api-id yqv4v90gj9 \
  --route-id s4t6xz3 \
  --authorization-type NONE
```

**Reason:** Frontend cannot provide IAM credentials for WebSocket connection. Changed to NONE for public access.

**Current State:**
- `$connect`: NONE ✅
- `$default`: NONE ✅
- `$disconnect`: NONE ✅

**Verification:**
```bash
aws apigatewayv2 get-routes --api-id yqv4v90gj9 \
  --query 'Items[*].[RouteKey,AuthorizationType]' \
  --output table
```

---

## 2. Lambda Function - Connect Handler

### Change: Updated handler and deployed new code

**Function Name:** `ai-therapy-platform-dev-websocket-connect`

**Commands:**
```bash
# Create deployment package
zip -j websocket_connect.zip backend/src/lambda_functions/websocket_connect_entry.py

# Update function code
aws lambda update-function-code \
  --function-name ai-therapy-platform-dev-websocket-connect \
  --zip-file fileb://websocket_connect.zip

# Update handler configuration
aws lambda update-function-configuration \
  --function-name ai-therapy-platform-dev-websocket-connect \
  --handler websocket_connect_entry.lambda_handler
```

**Previous Handler:** `websocket_handlers.connect_handler` ❌
**New Handler:** `websocket_connect_entry.lambda_handler` ✅

**Verification:**
```bash
aws lambda get-function-configuration \
  --function-name ai-therapy-platform-dev-websocket-connect \
  --query 'Handler' \
  --output text
```

---

## 3. Lambda Function - Default Handler

### Change: Updated handler and deployed new code with Nova Sonic 2

**Function Name:** `ai-therapy-platform-dev-websocket-default`

**Commands:**
```bash
# Create deployment package
zip -j websocket_default.zip backend/src/lambda_functions/websocket_default_entry.py

# Update function code
aws lambda update-function-code \
  --function-name ai-therapy-platform-dev-websocket-default \
  --zip-file fileb://websocket_default.zip

# Update handler configuration
aws lambda update-function-configuration \
  --function-name ai-therapy-platform-dev-websocket-default \
  --handler websocket_default_entry.lambda_handler
```

**Previous Handler:** `websocket_handlers.default_handler` ❌
**New Handler:** `websocket_default_entry.lambda_handler` ✅

**Features:**
- Amazon Nova Sonic 2 integration (`us.amazon.nova-sonic-v1:0`)
- Base64 audio processing
- Therapeutic system prompt
- Rate limiting (< 1 RPS)

**Verification:**
```bash
aws lambda get-function-configuration \
  --function-name ai-therapy-platform-dev-websocket-default \
  --query 'Handler' \
  --output text
```

---

## 4. Testing & Verification

### WebSocket Connection Test

**Test Script:** `test_websocket.py`

**Results:**
```
✅ WebSocket connection successful
✅ Control messages working (start_session)
✅ ACK messages received
✅ Welcome message from AI received
```

**Test Command:**
```bash
python3 test_websocket.py
```

### Lambda Logs

**View Connect Handler Logs:**
```bash
aws logs tail /aws/lambda/ai-therapy-platform-dev-websocket-connect --follow
```

**View Default Handler Logs:**
```bash
aws logs tail /aws/lambda/ai-therapy-platform-dev-websocket-default --follow
```

---

## 5. Current AWS Resources

### API Gateway WebSocket
- **API ID:** `yqv4v90gj9`
- **Endpoint:** `wss://yqv4v90gj9.execute-api.us-west-2.amazonaws.com/dev`
- **Stage:** `dev`
- **Region:** `us-west-2`

### Lambda Functions
1. **Connect Handler:**
   - Name: `ai-therapy-platform-dev-websocket-connect`
   - Handler: `websocket_connect_entry.lambda_handler`
   - Runtime: Python 3.11
   - Memory: 256 MB
   - Timeout: 30s

2. **Default Handler:**
   - Name: `ai-therapy-platform-dev-websocket-default`
   - Handler: `websocket_default_entry.lambda_handler`
   - Runtime: Python 3.11
   - Memory: 256 MB
   - Timeout: 30s

3. **Disconnect Handler:**
   - Name: `ai-therapy-platform-dev-websocket-disconnect`
   - Handler: `websocket_handlers.disconnect_handler`
   - Runtime: Python 3.11
   - Memory: 256 MB
   - Timeout: 30s

### DynamoDB Tables
- **Connections:** `ai-therapy-platform-dev-websocket-connections`
- **Sessions:** `ai-therapy-platform-dev-sessions`

### Cognito
- **User Pool ID:** `us-west-2_ASOPUuOOV`
- **Client ID:** `50bh1stem2eqiatfi4cg382rj8`

---

## 6. Rollback Instructions

If you need to rollback these changes:

### Rollback API Gateway Authorization:
```bash
aws apigatewayv2 update-route \
  --api-id yqv4v90gj9 \
  --route-id s4t6xz3 \
  --authorization-type AWS_IAM
```

### Rollback Lambda Handlers:
```bash
# Connect handler
aws lambda update-function-configuration \
  --function-name ai-therapy-platform-dev-websocket-connect \
  --handler websocket_handlers.connect_handler

# Default handler
aws lambda update-function-configuration \
  --function-name ai-therapy-platform-dev-websocket-default \
  --handler websocket_handlers.default_handler
```

---

## 7. Future Improvements

### Move to Infrastructure as Code (IaC)

To make these changes permanent in Terraform:

1. **Update `terraform/api_gateway.tf`:**
```hcl
resource "aws_apigatewayv2_route" "connect" {
  api_id    = aws_apigatewayv2_api.websocket.id
  route_key = "$connect"
  
  authorization_type = "NONE"  # Changed from AWS_IAM
  target = "integrations/${aws_apigatewayv2_integration.connect.id}"
}
```

2. **Update `terraform/lambda.tf`:**
```hcl
resource "aws_lambda_function" "websocket_connect" {
  # ...
  handler = "websocket_connect_entry.lambda_handler"  # Updated
  # ...
}

resource "aws_lambda_function" "websocket_default" {
  # ...
  handler = "websocket_default_entry.lambda_handler"  # Updated
  # ...
}
```

3. **Apply Terraform:**
```bash
cd terraform
terraform plan
terraform apply
```

---

## 8. Critical Notes

⚠️ **IMPORTANT:**
- All AWS accounts terminate at **23:00 on 15th January 2026**
- These manual changes will be lost when accounts terminate
- All code is saved in Git: https://github.com/work2fly/AWS-hackathon-man07/tree/develop
- To recreate, you must:
  1. Deploy infrastructure with Terraform
  2. Apply these manual changes via AWS CLI
  3. Deploy Lambda code

🏆 **Breaking Barriers UK 2026 compliant:**
- Region: us-west-2 ✅
- Permitted services only ✅
- Rate limiting implemented ✅
- No reserved Lambda environment variables ✅

---

**Last Updated:** 2026-01-14 21:20 UTC
**Time Remaining:** ~1 hour 40 minutes until account termination
**Status:** WebSocket working, ready for voice-to-voice testing
