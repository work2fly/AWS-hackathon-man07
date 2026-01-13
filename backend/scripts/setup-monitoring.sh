#!/bin/bash

# AI Therapy Platform - Monitoring Setup Script
# Breaking Barriers UK 2026 compliant monitoring configuration

set -e

REGION="us-west-2"
PROJECT_NAME="ai-therapy-platform"
ENVIRONMENT="dev"
DASHBOARD_NAME="${PROJECT_NAME}-${ENVIRONMENT}-dashboard"

echo "🚀 AI Therapy Platform - Monitoring Setup"
echo "🏆 Breaking Barriers UK 2026 compliant"
echo "=" * 50

# Check AWS credentials
echo "🔍 Checking AWS credentials..."
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ AWS credentials not configured"
    exit 1
fi

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "✅ AWS credentials valid (Account: $ACCOUNT_ID)"

# Create CloudWatch Dashboard
echo "📊 Creating CloudWatch Dashboard..."
DASHBOARD_BODY=$(cat backend/monitoring/dashboard_config.json)

aws cloudwatch put-dashboard \
    --dashboard-name "$DASHBOARD_NAME" \
    --dashboard-body "$DASHBOARD_BODY" \
    --region "$REGION"

echo "✅ CloudWatch Dashboard created: $DASHBOARD_NAME"

# Create CloudWatch Alarms
echo "🚨 Creating CloudWatch Alarms..."

# API Gateway 4XX Error Alarm
aws cloudwatch put-metric-alarm \
    --alarm-name "${PROJECT_NAME}-api-4xx-errors" \
    --alarm-description "API Gateway 4XX errors" \
    --metric-name "4XXError" \
    --namespace "AWS/ApiGateway" \
    --statistic "Sum" \
    --period 300 \
    --threshold 10 \
    --comparison-operator "GreaterThanThreshold" \
    --evaluation-periods 2 \
    --dimensions Name=ApiName,Value="${PROJECT_NAME}-rest-api" \
    --region "$REGION"

# API Gateway 5XX Error Alarm
aws cloudwatch put-metric-alarm \
    --alarm-name "${PROJECT_NAME}-api-5xx-errors" \
    --alarm-description "API Gateway 5XX errors" \
    --metric-name "5XXError" \
    --namespace "AWS/ApiGateway" \
    --statistic "Sum" \
    --period 300 \
    --threshold 5 \
    --comparison-operator "GreaterThanThreshold" \
    --evaluation-periods 2 \
    --dimensions Name=ApiName,Value="${PROJECT_NAME}-rest-api" \
    --region "$REGION"

# High Latency Alarm
aws cloudwatch put-metric-alarm \
    --alarm-name "${PROJECT_NAME}-api-latency" \
    --alarm-description "API Gateway high latency" \
    --metric-name "Latency" \
    --namespace "AWS/ApiGateway" \
    --statistic "Average" \
    --period 300 \
    --threshold 2000 \
    --comparison-operator "GreaterThanThreshold" \
    --evaluation-periods 2 \
    --dimensions Name=ApiName,Value="${PROJECT_NAME}-rest-api" \
    --region "$REGION"

# Red Flag Alert Alarm
aws cloudwatch put-metric-alarm \
    --alarm-name "${PROJECT_NAME}-red-flags-critical" \
    --alarm-description "Critical red flags detected" \
    --metric-name "RedFlagsDetected" \
    --namespace "AI-Therapy-Platform" \
    --statistic "Sum" \
    --period 60 \
    --threshold 1 \
    --comparison-operator "GreaterThanOrEqualToThreshold" \
    --evaluation-periods 1 \
    --dimensions Name=Severity,Value=critical \
    --region "$REGION"

echo "✅ CloudWatch Alarms created"

# Create Log Groups (if they don't exist)
echo "📝 Creating CloudWatch Log Groups..."

LOG_GROUPS=(
    "/aws/lambda/${PROJECT_NAME}"
    "/aws/apigateway/${PROJECT_NAME}-rest-api"
    "/aws/apigateway/${PROJECT_NAME}-websocket-api"
)

for LOG_GROUP in "${LOG_GROUPS[@]}"; do
    if ! aws logs describe-log-groups --log-group-name-prefix "$LOG_GROUP" --region "$REGION" | grep -q "$LOG_GROUP"; then
        aws logs create-log-group \
            --log-group-name "$LOG_GROUP" \
            --region "$REGION"
        
        # Set retention policy (7 days for hackathon)
        aws logs put-retention-policy \
            --log-group-name "$LOG_GROUP" \
            --retention-in-days 7 \
            --region "$REGION"
        
        echo "✅ Created log group: $LOG_GROUP"
    else
        echo "ℹ️  Log group already exists: $LOG_GROUP"
    fi
done

# Create SNS Topic for Alerts (optional for hackathon)
echo "📢 Creating SNS Topic for alerts..."
TOPIC_ARN=$(aws sns create-topic \
    --name "${PROJECT_NAME}-alerts" \
    --region "$REGION" \
    --query 'TopicArn' \
    --output text)

echo "✅ SNS Topic created: $TOPIC_ARN"

# Display monitoring URLs
echo ""
echo "📊 Monitoring Resources Created:"
echo "================================"
echo "CloudWatch Dashboard: https://${REGION}.console.aws.amazon.com/cloudwatch/home?region=${REGION}#dashboards:name=${DASHBOARD_NAME}"
echo "CloudWatch Alarms: https://${REGION}.console.aws.amazon.com/cloudwatch/home?region=${REGION}#alarmsV2:"
echo "CloudWatch Logs: https://${REGION}.console.aws.amazon.com/cloudwatch/home?region=${REGION}#logsV2:log-groups"
echo "SNS Topic ARN: $TOPIC_ARN"

echo ""
echo "🎉 Monitoring setup completed successfully!"
echo "🏆 Breaking Barriers UK 2026 compliant monitoring configured"
echo ""
echo "⚠️  Remember: AWS accounts terminate at 23:00 on 15th January 2026"
echo "   Monitor your usage and save important data before the deadline!"