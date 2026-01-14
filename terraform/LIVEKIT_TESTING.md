# LiveKit Infrastructure Testing Guide
🏆 Breaking Barriers UK 2026 Hackathon

## Overview

This guide provides comprehensive testing procedures for the LiveKit infrastructure deployment. Follow these steps to verify that all components are working correctly.

## Prerequisites

1. LiveKit infrastructure deployed via Terraform
2. AWS CLI configured with appropriate credentials
3. Python 3.8+ with boto3 installed
4. (Optional) livekit-api Python package for token generation testing

## Test Scripts

### 1. Connectivity Test Script

Tests basic infrastructure connectivity and health.

```bash
cd terraform/scripts
./test-livekit-connectivity.sh
```

**What it tests:**
- ALB reachability on port 7880
- ECS service status and running tasks
- ALB target group health
- Redis endpoint configuration
- Secrets Manager access
- CloudWatch Logs configuration

**Expected output:**
```
🏆 Breaking Barriers UK 2026 - LiveKit Connectivity Test
========================================================

📡 Retrieving LiveKit server information...
✅ LiveKit Server URL: ws://livekit-alb-123456789.us-west-2.elb.amazonaws.com:7880
✅ ALB DNS: livekit-alb-123456789.us-west-2.elb.amazonaws.com

🔍 Test 1: Checking ALB reachability...
✅ ALB is reachable on port 7880

🔍 Test 2: Checking ECS service status...
   Status: ACTIVE
   Running Tasks: 1 / 1
✅ ECS service is healthy

🔍 Test 3: Checking ALB target group health...
   Target Health: healthy
✅ Target group is healthy

🔍 Test 4: Checking Redis connectivity...
✅ Redis endpoint: ai-therapy-platform-dev-livekit.abc123.0001.usw2.cache.amazonaws.com

🔍 Test 5: Checking Secrets Manager...
✅ Secrets Manager configured correctly
   API Key Secret: ai-therapy-platform-dev-livekit-key-only

🔍 Test 6: Checking CloudWatch Logs...
✅ CloudWatch log group exists: /ecs/ai-therapy-platform-dev-livekit
   Latest log stream: livekit/livekit/abc123...
```

### 2. Token Generation Test Script

Tests LiveKit API authentication and token generation.

**Installation:**
```bash
pip install livekit-api pyjwt
```

**Run test:**
```bash
cd terraform/scripts
python3 test-livekit-token.py
```

**What it tests:**
- Terraform output retrieval
- Secrets Manager credential access
- LiveKit token generation
- Token validation and decoding

**Expected output:**
```
🏆 Breaking Barriers UK 2026 - LiveKit Token Generation Test
============================================================

📡 Retrieving configuration from Terraform...
✅ LiveKit Server URL: ws://livekit-alb-123456789.us-west-2.elb.amazonaws.com:7880

🔐 Retrieving API credentials from Secrets Manager...
✅ API credentials retrieved successfully
   API Key: abcd1234...xyz9

🎫 Generating test token...
✅ Token generated successfully!

Token Details:
   Identity: test-user-123
   Room: test-room
   Permissions: publish, subscribe
   Expires: 2026-01-15 14:30:00

JWT Token (first 50 chars):
   eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3M...

🔍 Validating token...
✅ Token is valid!
   Subject: test-user-123
   Video grants: {'roomJoin': True, 'room': 'test-room', ...}
```

## Manual Testing Procedures

### Test 1: Verify ECS Service

```bash
# Get cluster and service names
CLUSTER=$(terraform output -json livekit_infrastructure | jq -r '.ecs_cluster_name')
SERVICE=$(terraform output -json livekit_infrastructure | jq -r '.ecs_service_name')

# Check service status
aws ecs describe-services \
  --cluster $CLUSTER \
  --services $SERVICE \
  --region us-west-2 \
  --query 'services[0].[status,runningCount,desiredCount]' \
  --output table
```

**Expected:** Status=ACTIVE, runningCount=desiredCount

### Test 2: Check Task Health

```bash
# List running tasks
aws ecs list-tasks \
  --cluster $CLUSTER \
  --service-name $SERVICE \
  --region us-west-2

# Describe task (replace TASK_ARN with actual ARN)
aws ecs describe-tasks \
  --cluster $CLUSTER \
  --tasks TASK_ARN \
  --region us-west-2 \
  --query 'tasks[0].[lastStatus,healthStatus,containers[0].healthStatus]' \
  --output table
```

**Expected:** lastStatus=RUNNING, healthStatus=HEALTHY

### Test 3: Verify Load Balancer

```bash
# Get ALB DNS name
ALB_DNS=$(terraform output -json livekit_infrastructure | jq -r '.alb_dns_name')

# Test HTTP endpoint
curl -v "http://${ALB_DNS}:7880/"

# Expected: HTTP 200 or 404 (LiveKit root may not have content)
# Important: Connection should succeed, not timeout
```

### Test 4: Check Target Group Health

```bash
# Get target group ARN
TG_ARN=$(aws elbv2 describe-target-groups \
  --region us-west-2 \
  --query "TargetGroups[?contains(TargetGroupName, 'livekit-http')].TargetGroupArn" \
  --output text)

# Check target health
aws elbv2 describe-target-health \
  --target-group-arn $TG_ARN \
  --region us-west-2 \
  --query 'TargetHealthDescriptions[*].[Target.Id,TargetHealth.State,TargetHealth.Reason]' \
  --output table
```

**Expected:** State=healthy

### Test 5: Verify Redis Connectivity

```bash
# Get Redis endpoint
REDIS_ENDPOINT=$(terraform output -json livekit_infrastructure | jq -r '.redis_endpoint')

echo "Redis endpoint: $REDIS_ENDPOINT"

# Note: Redis is in private subnet, so direct connection from local machine won't work
# Verify via ECS task logs that LiveKit connects to Redis successfully
```

### Test 6: Check CloudWatch Logs

```bash
# Tail logs in real-time
aws logs tail /ecs/ai-therapy-platform-dev-livekit \
  --follow \
  --region us-west-2

# Look for:
# - "starting LiveKit server" - server startup
# - "redis connected" - Redis connection success
# - "server listening" - server ready to accept connections
```

### Test 7: Verify Secrets Access

```bash
# Get secret ARNs
API_KEY_ARN=$(terraform output -json livekit_api_credentials | jq -r '.api_key_secret_arn')
API_SECRET_ARN=$(terraform output -json livekit_api_credentials | jq -r '.api_secret_secret_arn')

# Retrieve secrets (requires appropriate IAM permissions)
aws secretsmanager get-secret-value \
  --secret-id $API_KEY_ARN \
  --region us-west-2 \
  --query SecretString \
  --output text

aws secretsmanager get-secret-value \
  --secret-id $API_SECRET_ARN \
  --region us-west-2 \
  --query SecretString \
  --output text
```

**Expected:** Both commands return secret values

### Test 8: Security Group Validation

```bash
# Check LiveKit ECS security group
aws ec2 describe-security-groups \
  --filters "Name=tag:Name,Values=ai-therapy-platform-dev-livekit-ecs-sg" \
  --region us-west-2 \
  --query 'SecurityGroups[0].IpPermissions[*].[FromPort,ToPort,IpProtocol]' \
  --output table
```

**Expected ports:**
- 7880 (TCP) - LiveKit HTTP
- 7881 (TCP) - LiveKit HTTPS
- 50000-60000 (UDP) - WebRTC
- 50000-60000 (TCP) - WebRTC fallback

## Integration Testing

### Test 9: End-to-End Token Flow

Create a test Lambda function to generate tokens:

```python
import json
import boto3
from livekit import api
from datetime import timedelta

def lambda_handler(event, context):
    # Get credentials from Secrets Manager
    secrets = boto3.client('secretsmanager')
    
    api_key = secrets.get_secret_value(
        SecretId='ai-therapy-platform-dev-livekit-key-only'
    )['SecretString']
    
    api_secret = secrets.get_secret_value(
        SecretId='ai-therapy-platform-dev-livekit-api-secret'
    )['SecretString']
    
    # Generate token
    token = api.AccessToken(api_key, api_secret)
    token.with_identity(event['userId'])
    token.with_name(event['userName'])
    token.with_grants(api.VideoGrants(
        room_join=True,
        room=event['roomName'],
        can_publish=True,
        can_subscribe=True,
    ))
    token.with_ttl(timedelta(hours=1))
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'token': token.to_jwt(),
            'serverUrl': 'ws://your-alb-dns:7880'
        })
    }
```

### Test 10: Client Connection Test

Use the LiveKit CLI or SDK to test client connection:

```bash
# Install LiveKit CLI
npm install -g @livekit/cli

# Test connection (replace with your values)
livekit-cli join-room \
  --url ws://your-alb-dns:7880 \
  --token YOUR_GENERATED_TOKEN \
  --room test-room
```

## Troubleshooting

### Issue: ECS Tasks Not Starting

**Symptoms:** runningCount = 0, tasks keep restarting

**Check:**
1. CloudWatch logs for error messages
2. Task definition CPU/memory limits
3. IAM role permissions
4. Secrets Manager access

**Solution:**
```bash
# Check task stopped reason
aws ecs describe-tasks \
  --cluster $CLUSTER \
  --tasks $(aws ecs list-tasks --cluster $CLUSTER --service-name $SERVICE --region us-west-2 --query 'taskArns[0]' --output text) \
  --region us-west-2 \
  --query 'tasks[0].stoppedReason'
```

### Issue: Target Group Unhealthy

**Symptoms:** Target health = unhealthy or initial

**Check:**
1. Health check path (/health)
2. Security group rules
3. Container port mapping
4. Application logs

**Solution:**
```bash
# Check health check configuration
aws elbv2 describe-target-groups \
  --target-group-arns $TG_ARN \
  --region us-west-2 \
  --query 'TargetGroups[0].HealthCheckPath'

# Verify container is listening on port 7880
aws logs tail /ecs/ai-therapy-platform-dev-livekit --region us-west-2 | grep "listening"
```

### Issue: Redis Connection Failed

**Symptoms:** Logs show "redis connection failed"

**Check:**
1. Redis security group allows traffic from ECS tasks
2. Redis endpoint is correct
3. Redis is in same VPC as ECS tasks

**Solution:**
```bash
# Verify security group rules
aws ec2 describe-security-groups \
  --filters "Name=tag:Name,Values=ai-therapy-platform-dev-redis-sg" \
  --region us-west-2 \
  --query 'SecurityGroups[0].IpPermissions'
```

### Issue: Cannot Generate Tokens

**Symptoms:** Secrets Manager access denied

**Check:**
1. IAM role has secretsmanager:GetSecretValue permission
2. Secret ARNs are correct
3. Secrets exist in us-west-2 region

**Solution:**
```bash
# Verify IAM role policy
aws iam get-role-policy \
  --role-name ai-therapy-platform-dev-ecs-task-execution-role \
  --policy-name ai-therapy-platform-dev-ecs-secrets-access \
  --region us-west-2
```

## Performance Testing

### Load Test Configuration

For hackathon, test with:
- 5-10 concurrent connections
- 1-2 minute session duration
- Monitor CPU and memory usage

```bash
# Monitor ECS service metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ServiceName,Value=$SERVICE Name=ClusterName,Value=$CLUSTER \
  --start-time $(date -u -d '10 minutes ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 60 \
  --statistics Average \
  --region us-west-2
```

## Success Criteria

✅ All automated tests pass
✅ ECS service shows ACTIVE status with healthy tasks
✅ Target groups show healthy targets
✅ CloudWatch logs show successful startup
✅ Token generation succeeds
✅ Client can connect to LiveKit server
✅ WebRTC audio streams successfully

## Next Steps

After successful testing:
1. Proceed to Task 2: Implement LiveKit Agent with Nova Sonic
2. Integrate with Lambda functions for token generation
3. Connect frontend React application
4. Test end-to-end therapy session flow

## Resources

- [LiveKit Server Documentation](https://docs.livekit.io/deploy/)
- [AWS ECS Troubleshooting](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/troubleshooting.html)
- [LiveKit API Documentation](https://docs.livekit.io/server-sdk/)

---

🏆 **Breaking Barriers UK 2026 Compliant**
- ✅ All tests use us-west-2 region
- ✅ Follows AWS best practices
- ✅ Comprehensive monitoring and logging
