# LiveKit Infrastructure Deployment Guide
🏆 Breaking Barriers UK 2026 Hackathon

## Overview

This guide covers the deployment of LiveKit server infrastructure on AWS ECS for the AI Therapy Platform. LiveKit provides real-time WebRTC audio communication between clients and the AI therapy agent.

## Architecture Components

### Core Infrastructure
- **VPC**: Multi-AZ VPC with public and private subnets
- **ECS Cluster**: Fargate-based cluster for LiveKit server
- **Application Load Balancer**: Routes HTTP/HTTPS traffic to LiveKit
- **Network Load Balancer**: Routes WebRTC UDP traffic
- **ElastiCache Redis**: State management for distributed LiveKit instances
- **Secrets Manager**: Secure storage of LiveKit API credentials
- **DynamoDB**: LiveKitRooms table for session tracking

### Security
- **Security Groups**: Configured for LiveKit ports (7880, 7881, 50000-60000)
- **Encryption**: TLS in transit, AES-256 at rest
- **IAM Roles**: Least-privilege access for ECS tasks

## Prerequisites

1. AWS CLI configured with appropriate credentials
2. Terraform >= 1.12 installed
3. Access to us-west-2 region (Breaking Barriers UK 2026 requirement)

## Deployment Steps

### 1. Initialize Terraform

```bash
cd terraform
terraform init -backend-config=backend.hcl
```

### 2. Review Configuration

Check `terraform.tfvars` for environment-specific settings:

```hcl
aws_region  = "us-west-2"
environment = "dev"
project_name = "ai-therapy-platform"

# Enable encryption (required for hackathon)
enable_encryption = true

# Disable deletion protection for easy cleanup
enable_deletion_protection = false
```

### 3. Plan Deployment

```bash
terraform plan -out=tfplan
```

Review the plan to ensure:
- VPC and networking resources are created
- ECS cluster and task definition are configured
- Load balancers are set up correctly
- Security groups allow required ports
- ElastiCache Redis is provisioned
- Secrets Manager stores API credentials

### 4. Apply Configuration

```bash
terraform apply tfplan
```

This will create:
- VPC with 2 public and 2 private subnets
- NAT Gateways for private subnet internet access
- ECS cluster with LiveKit task definition
- Application Load Balancer (ALB) for HTTP/HTTPS
- Network Load Balancer (NLB) for WebRTC UDP
- ElastiCache Redis cluster
- Security groups for all components
- Secrets Manager secrets for API keys
- DynamoDB table for room tracking

### 5. Verify Deployment

```bash
# Get LiveKit server URL
terraform output livekit_connection_info

# Check ECS service status
aws ecs describe-services \
  --cluster $(terraform output -raw livekit_infrastructure | jq -r '.ecs_cluster_name') \
  --services $(terraform output -raw livekit_infrastructure | jq -r '.ecs_service_name') \
  --region us-west-2

# Test LiveKit health endpoint
LIVEKIT_URL=$(terraform output -json livekit_connection_info | jq -r '.server_url')
curl ${LIVEKIT_URL}/health
```

## Configuration

### LiveKit Server Configuration

The LiveKit server is configured via environment variables in the ECS task definition:

- `REDIS_HOST`: ElastiCache Redis endpoint
- `REDIS_PORT`: Redis port (6379)
- `LIVEKIT_PORT`: HTTP port (7880)
- `LIVEKIT_RTC_PORT_RANGE_START`: WebRTC UDP start port (50000)
- `LIVEKIT_RTC_PORT_RANGE_END`: WebRTC UDP end port (60000)
- `LIVEKIT_KEYS`: API key and secret from Secrets Manager

### Auto-Scaling

The ECS service is configured with auto-scaling based on:
- **CPU Utilization**: Target 70%
- **Memory Utilization**: Target 80%
- **Min Tasks**: 1
- **Max Tasks**: 4

### Monitoring

CloudWatch logs are configured for:
- ECS task logs: `/ecs/ai-therapy-platform-dev-livekit`
- Log retention: 7 days (configurable)

## Accessing LiveKit

### Server URLs

After deployment, get the server URLs:

```bash
terraform output livekit_connection_info
```

Output:
```json
{
  "server_url": "ws://livekit-alb-123456789.us-west-2.elb.amazonaws.com:7880",
  "server_url_secure": "wss://livekit-alb-123456789.us-west-2.elb.amazonaws.com:7881"
}
```

### API Credentials

Retrieve API credentials from Secrets Manager:

```bash
# Get API key
aws secretsmanager get-secret-value \
  --secret-id ai-therapy-platform-dev-livekit-key-only \
  --region us-west-2 \
  --query SecretString \
  --output text

# Get API secret
aws secretsmanager get-secret-value \
  --secret-id ai-therapy-platform-dev-livekit-api-secret \
  --region us-west-2 \
  --query SecretString \
  --output text
```

## Integration with Backend

### Lambda Environment Variables

Add these to Lambda functions that need to generate LiveKit tokens:

```python
import os
import boto3

# Get LiveKit configuration
LIVEKIT_SERVER_URL = os.environ['LIVEKIT_SERVER_URL']
LIVEKIT_API_KEY_SECRET = os.environ['LIVEKIT_API_KEY_SECRET']
LIVEKIT_API_SECRET_SECRET = os.environ['LIVEKIT_API_SECRET_SECRET']

# Retrieve credentials from Secrets Manager
secrets_client = boto3.client('secretsmanager')
api_key = secrets_client.get_secret_value(SecretId=LIVEKIT_API_KEY_SECRET)['SecretString']
api_secret = secrets_client.get_secret_value(SecretId=LIVEKIT_API_SECRET_SECRET)['SecretString']
```

### DynamoDB Room Tracking

The `livekit-rooms` table tracks active LiveKit rooms:

```python
import boto3
from datetime import datetime, timedelta

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ai-therapy-platform-dev-livekit-rooms')

# Create room entry
table.put_item(
    Item={
        'roomName': f'session_{session_id}',
        'sessionId': session_id,
        'clientId': client_id,
        'agentId': agent_id,
        'status': 'active',
        'createdAt': datetime.utcnow().isoformat(),
        'ttl': int((datetime.utcnow() + timedelta(hours=24)).timestamp()),
        'participantCount': 0
    }
)
```

## Troubleshooting

### ECS Task Not Starting

Check CloudWatch logs:
```bash
aws logs tail /ecs/ai-therapy-platform-dev-livekit --follow --region us-west-2
```

Common issues:
- Redis connection failure: Check security groups
- Secrets access denied: Verify IAM role permissions
- Port conflicts: Ensure security groups allow required ports

### Load Balancer Health Checks Failing

Check target group health:
```bash
aws elbv2 describe-target-health \
  --target-group-arn $(terraform output -json livekit_infrastructure | jq -r '.alb_target_group_arn') \
  --region us-west-2
```

### WebRTC Connection Issues

Verify security groups allow UDP ports 50000-60000:
```bash
aws ec2 describe-security-groups \
  --filters "Name=tag:Name,Values=ai-therapy-platform-dev-livekit-ecs-sg" \
  --region us-west-2
```

## Cost Optimization

### Hackathon Configuration
- **ECS Tasks**: 1 vCPU, 2GB RAM (Fargate)
- **Redis**: cache.t3.micro (smallest instance)
- **NAT Gateways**: 2 (for high availability)
- **Load Balancers**: ALB + NLB

### Estimated Costs (24 hours)
- ECS Fargate: ~$1.50/day
- ElastiCache: ~$0.50/day
- NAT Gateways: ~$2.00/day
- Load Balancers: ~$1.50/day
- **Total**: ~$5.50/day

## Cleanup

To destroy all LiveKit infrastructure:

```bash
cd terraform
terraform destroy -target=aws_ecs_service.livekit
terraform destroy -target=aws_ecs_cluster.livekit
terraform destroy -target=aws_lb.livekit
terraform destroy -target=aws_lb.livekit_webrtc
terraform destroy -target=aws_elasticache_cluster.livekit
terraform destroy -target=aws_vpc.main
terraform destroy
```

**Note**: Account terminates at 23:00 on 15th January 2026. Ensure all work is saved to Git before this time!

## Next Steps

1. **Task 1.2**: Configure LiveKit authentication and test connectivity
2. **Task 2**: Implement LiveKit Agent with Nova Sonic integration
3. **Task 3**: Add safety guardrails and red flag detection
4. **Task 4**: Build sentiment analysis and progress tracking

## Resources

- [LiveKit Documentation](https://docs.livekit.io/)
- [LiveKit Server Configuration](https://docs.livekit.io/deploy/)
- [AWS ECS Best Practices](https://docs.aws.amazon.com/AmazonECS/latest/bestpracticesguide/)
- [Breaking Barriers UK 2026 Rules](../breaking-barriers-uk-2026-rules.md)

---

🏆 **Breaking Barriers UK 2026 Compliant**
- ✅ Deployed to us-west-2 region
- ✅ Uses permitted AWS services (ECS, ElastiCache, ALB, NLB)
- ✅ Encryption enabled for data at rest and in transit
- ✅ Open-source LiveKit (no licensing issues)
