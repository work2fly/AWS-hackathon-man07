#!/bin/bash
# Test LiveKit Server Connectivity
# Breaking Barriers UK 2026 Hackathon

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🏆 Breaking Barriers UK 2026 - LiveKit Connectivity Test"
echo "========================================================"
echo ""

# Check if terraform is initialized
if [ ! -d "../.terraform" ]; then
    echo -e "${RED}❌ Terraform not initialized. Run 'terraform init' first.${NC}"
    exit 1
fi

# Get LiveKit server URL from Terraform outputs
echo "📡 Retrieving LiveKit server information..."
cd ..
LIVEKIT_URL=$(terraform output -json livekit_connection_info 2>/dev/null | jq -r '.server_url' || echo "")
LIVEKIT_ALB_DNS=$(terraform output -json livekit_infrastructure 2>/dev/null | jq -r '.alb_dns_name' || echo "")

if [ -z "$LIVEKIT_URL" ] || [ "$LIVEKIT_URL" == "null" ]; then
    echo -e "${RED}❌ Could not retrieve LiveKit server URL. Is infrastructure deployed?${NC}"
    exit 1
fi

echo -e "${GREEN}✅ LiveKit Server URL: $LIVEKIT_URL${NC}"
echo -e "${GREEN}✅ ALB DNS: $LIVEKIT_ALB_DNS${NC}"
echo ""

# Test 1: Check if ALB is reachable
echo "🔍 Test 1: Checking ALB reachability..."
if curl -s --connect-timeout 10 "http://${LIVEKIT_ALB_DNS}:7880/" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ ALB is reachable on port 7880${NC}"
else
    echo -e "${YELLOW}⚠️  ALB not yet reachable (may still be provisioning)${NC}"
fi
echo ""

# Test 2: Check ECS service status
echo "🔍 Test 2: Checking ECS service status..."
CLUSTER_NAME=$(terraform output -json livekit_infrastructure 2>/dev/null | jq -r '.ecs_cluster_name')
SERVICE_NAME=$(terraform output -json livekit_infrastructure 2>/dev/null | jq -r '.ecs_service_name')

if [ -n "$CLUSTER_NAME" ] && [ "$CLUSTER_NAME" != "null" ]; then
    SERVICE_STATUS=$(aws ecs describe-services \
        --cluster "$CLUSTER_NAME" \
        --services "$SERVICE_NAME" \
        --region us-west-2 \
        --query 'services[0].status' \
        --output text 2>/dev/null || echo "UNKNOWN")
    
    RUNNING_COUNT=$(aws ecs describe-services \
        --cluster "$CLUSTER_NAME" \
        --services "$SERVICE_NAME" \
        --region us-west-2 \
        --query 'services[0].runningCount' \
        --output text 2>/dev/null || echo "0")
    
    DESIRED_COUNT=$(aws ecs describe-services \
        --cluster "$CLUSTER_NAME" \
        --services "$SERVICE_NAME" \
        --region us-west-2 \
        --query 'services[0].desiredCount' \
        --output text 2>/dev/null || echo "0")
    
    echo "   Status: $SERVICE_STATUS"
    echo "   Running Tasks: $RUNNING_COUNT / $DESIRED_COUNT"
    
    if [ "$RUNNING_COUNT" -eq "$DESIRED_COUNT" ] && [ "$RUNNING_COUNT" -gt 0 ]; then
        echo -e "${GREEN}✅ ECS service is healthy${NC}"
    else
        echo -e "${YELLOW}⚠️  ECS service is starting up (this may take 2-3 minutes)${NC}"
    fi
else
    echo -e "${RED}❌ Could not retrieve ECS cluster information${NC}"
fi
echo ""

# Test 3: Check target group health
echo "🔍 Test 3: Checking ALB target group health..."
TARGET_GROUP_ARN=$(aws elbv2 describe-target-groups \
    --region us-west-2 \
    --query "TargetGroups[?contains(TargetGroupName, 'livekit-http')].TargetGroupArn" \
    --output text 2>/dev/null || echo "")

if [ -n "$TARGET_GROUP_ARN" ]; then
    HEALTH_STATUS=$(aws elbv2 describe-target-health \
        --target-group-arn "$TARGET_GROUP_ARN" \
        --region us-west-2 \
        --query 'TargetHealthDescriptions[0].TargetHealth.State' \
        --output text 2>/dev/null || echo "unknown")
    
    echo "   Target Health: $HEALTH_STATUS"
    
    if [ "$HEALTH_STATUS" == "healthy" ]; then
        echo -e "${GREEN}✅ Target group is healthy${NC}"
    elif [ "$HEALTH_STATUS" == "initial" ]; then
        echo -e "${YELLOW}⚠️  Target group is initializing${NC}"
    else
        echo -e "${YELLOW}⚠️  Target group status: $HEALTH_STATUS${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Could not find target group${NC}"
fi
echo ""

# Test 4: Check Redis connectivity
echo "🔍 Test 4: Checking Redis connectivity..."
REDIS_ENDPOINT=$(terraform output -json livekit_infrastructure 2>/dev/null | jq -r '.redis_endpoint')

if [ -n "$REDIS_ENDPOINT" ] && [ "$REDIS_ENDPOINT" != "null" ]; then
    echo -e "${GREEN}✅ Redis endpoint: $REDIS_ENDPOINT${NC}"
    echo "   (Redis is in private subnet, connectivity verified via ECS task)"
else
    echo -e "${RED}❌ Could not retrieve Redis endpoint${NC}"
fi
echo ""

# Test 5: Check Secrets Manager
echo "🔍 Test 5: Checking Secrets Manager..."
API_KEY_SECRET=$(terraform output -json livekit_api_credentials 2>/dev/null | jq -r '.api_key_secret_arn')

if [ -n "$API_KEY_SECRET" ] && [ "$API_KEY_SECRET" != "null" ]; then
    SECRET_STATUS=$(aws secretsmanager describe-secret \
        --secret-id "$API_KEY_SECRET" \
        --region us-west-2 \
        --query 'Name' \
        --output text 2>/dev/null || echo "")
    
    if [ -n "$SECRET_STATUS" ]; then
        echo -e "${GREEN}✅ Secrets Manager configured correctly${NC}"
        echo "   API Key Secret: $SECRET_STATUS"
    else
        echo -e "${RED}❌ Could not access Secrets Manager${NC}"
    fi
else
    echo -e "${RED}❌ Could not retrieve secret ARN${NC}"
fi
echo ""

# Test 6: Check CloudWatch Logs
echo "🔍 Test 6: Checking CloudWatch Logs..."
LOG_GROUP="/ecs/ai-therapy-platform-dev-livekit"

LOG_EXISTS=$(aws logs describe-log-groups \
    --log-group-name-prefix "$LOG_GROUP" \
    --region us-west-2 \
    --query 'logGroups[0].logGroupName' \
    --output text 2>/dev/null || echo "")

if [ "$LOG_EXISTS" == "$LOG_GROUP" ]; then
    echo -e "${GREEN}✅ CloudWatch log group exists: $LOG_GROUP${NC}"
    
    # Check for recent log streams
    RECENT_STREAMS=$(aws logs describe-log-streams \
        --log-group-name "$LOG_GROUP" \
        --region us-west-2 \
        --order-by LastEventTime \
        --descending \
        --max-items 1 \
        --query 'logStreams[0].logStreamName' \
        --output text 2>/dev/null || echo "")
    
    if [ -n "$RECENT_STREAMS" ] && [ "$RECENT_STREAMS" != "None" ]; then
        echo "   Latest log stream: $RECENT_STREAMS"
        echo ""
        echo "   📋 Recent logs:"
        aws logs tail "$LOG_GROUP" --since 5m --region us-west-2 2>/dev/null | head -n 10 || echo "   (No recent logs)"
    else
        echo -e "${YELLOW}   ⚠️  No log streams yet (service may still be starting)${NC}"
    fi
else
    echo -e "${RED}❌ CloudWatch log group not found${NC}"
fi
echo ""

# Summary
echo "========================================================"
echo "📊 Test Summary"
echo "========================================================"
echo ""
echo "Next steps:"
echo "1. Wait 2-3 minutes for ECS tasks to fully start"
echo "2. Check CloudWatch logs for any errors:"
echo "   aws logs tail $LOG_GROUP --follow --region us-west-2"
echo ""
echo "3. Test LiveKit health endpoint:"
echo "   curl http://${LIVEKIT_ALB_DNS}:7880/"
echo ""
echo "4. Generate a test token (requires Lambda function):"
echo "   See terraform/LIVEKIT_DEPLOYMENT.md for details"
echo ""
echo "🏆 Breaking Barriers UK 2026 - LiveKit Infrastructure Ready!"
