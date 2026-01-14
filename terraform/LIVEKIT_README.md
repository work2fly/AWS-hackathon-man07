# LiveKit Infrastructure for AI Therapy Platform
🏆 Breaking Barriers UK 2026 Hackathon

## Overview

This directory contains Terraform infrastructure code for deploying LiveKit server on AWS ECS, providing real-time WebRTC audio communication for the AI Therapy Platform.

## What is LiveKit?

LiveKit is an open-source platform for building real-time voice, video, and AI applications. It provides:
- WebRTC-based low-latency audio/video
- Built-in voice activity detection
- Automatic noise suppression
- Turn detection for natural conversations
- Official AWS Nova Sonic 2 integration

## Architecture

```
Client (React + LiveKit SDK)
    ↓ WebRTC
Application Load Balancer (ports 7880, 7881)
    ↓
ECS Fargate Tasks (LiveKit Server)
    ↓
ElastiCache Redis (state management)
```

## Quick Start

### 1. Deploy Infrastructure

```bash
# Initialize Terraform
terraform init -backend-config=backend.hcl

# Review plan
terraform plan -out=tfplan

# Deploy
terraform apply tfplan
```

### 2. Verify Deployment

```bash
# Run connectivity tests
cd scripts
./test-livekit-connectivity.sh

# Test token generation
pip install livekit-api pyjwt
python3 test-livekit-token.py
```

### 3. Get Connection Info

```bash
# Get server URL
terraform output -json livekit_connection_info

# Get API credentials
terraform output -json livekit_api_credentials
```

## Files Structure

### Terraform Configuration
- `vpc.tf` - VPC, subnets, NAT gateways, routing
- `security_groups.tf` - Security groups for ALB, ECS, Redis
- `elasticache.tf` - Redis cluster for LiveKit state
- `ecs_livekit.tf` - ECS cluster, task definition, service
- `alb_livekit.tf` - Application and Network Load Balancers
- `secrets_livekit.tf` - Secrets Manager for API credentials
- `dynamodb.tf` - DynamoDB tables (includes LiveKitRooms)
- `outputs.tf` - Terraform outputs for integration

### Configuration
- `livekit_config/livekit.yaml` - LiveKit server configuration template

### Documentation
- `LIVEKIT_DEPLOYMENT.md` - Detailed deployment guide
- `LIVEKIT_TESTING.md` - Testing procedures and troubleshooting
- `VALIDATION_CHECKLIST.md` - Pre/post-deployment validation
- `LIVEKIT_README.md` - This file

### Scripts
- `scripts/test-livekit-connectivity.sh` - Automated connectivity tests
- `scripts/test-livekit-token.py` - Token generation tests

## Key Resources Created

### Networking
- 1 VPC (10.0.0.0/16)
- 2 Public Subnets
- 2 Private Subnets
- 2 NAT Gateways
- 1 Internet Gateway

### Compute
- 1 ECS Cluster
- 1 ECS Service (1-4 tasks)
- 1 Task Definition (1 vCPU, 2GB RAM)

### Load Balancing
- 1 Application Load Balancer (HTTP/HTTPS)
- 1 Network Load Balancer (WebRTC UDP)
- 2 Target Groups

### Data
- 1 ElastiCache Redis Cluster (cache.t3.micro)
- 1 DynamoDB Table (LiveKitRooms)

### Security
- 3 Security Groups (ALB, ECS, Redis)
- 3 Secrets Manager Secrets
- 2 IAM Roles (Task Execution, Task)

### Monitoring
- 1 CloudWatch Log Group
- Container Insights (optional)

## Configuration

### Environment Variables

Set in `terraform.tfvars`:

```hcl
aws_region  = "us-west-2"
environment = "dev"
project_name = "ai-therapy-platform"
enable_encryption = true
enable_deletion_protection = false
```

### LiveKit Configuration

Key settings in ECS task definition:
- `REDIS_HOST` - ElastiCache endpoint
- `LIVEKIT_PORT` - HTTP port (7880)
- `LIVEKIT_RTC_PORT_RANGE_START` - WebRTC start (50000)
- `LIVEKIT_RTC_PORT_RANGE_END` - WebRTC end (60000)
- `LIVEKIT_KEYS` - API credentials from Secrets Manager

## Integration

### Backend Lambda Functions

Generate LiveKit tokens:

```python
import boto3
from livekit import api
from datetime import timedelta

# Get credentials
secrets = boto3.client('secretsmanager')
api_key = secrets.get_secret_value(
    SecretId='ai-therapy-platform-dev-livekit-key-only'
)['SecretString']
api_secret = secrets.get_secret_value(
    SecretId='ai-therapy-platform-dev-livekit-api-secret'
)['SecretString']

# Generate token
token = api.AccessToken(api_key, api_secret)
token.with_identity(user_id)
token.with_grants(api.VideoGrants(
    room_join=True,
    room=room_name,
    can_publish=True,
    can_subscribe=True,
))
token.with_ttl(timedelta(hours=1))
jwt_token = token.to_jwt()
```

### Frontend React Application

Connect to LiveKit:

```typescript
import { LiveKitRoom } from '@livekit/components-react';

function TherapySession() {
  const { token, serverUrl } = useLiveKitToken();
  
  return (
    <LiveKitRoom
      token={token}
      serverUrl={serverUrl}
      connect={true}
      audio={true}
      video={false}
    >
      <VoiceAssistantUI />
    </LiveKitRoom>
  );
}
```

## Monitoring

### CloudWatch Logs

```bash
# Tail logs in real-time
aws logs tail /ecs/ai-therapy-platform-dev-livekit \
  --follow --region us-west-2

# Search for errors
aws logs filter-log-events \
  --log-group-name /ecs/ai-therapy-platform-dev-livekit \
  --filter-pattern "ERROR" \
  --region us-west-2
```

### ECS Service Metrics

```bash
# Check service status
aws ecs describe-services \
  --cluster ai-therapy-platform-dev-livekit-cluster \
  --services ai-therapy-platform-dev-livekit-service \
  --region us-west-2
```

### Load Balancer Health

```bash
# Check target health
aws elbv2 describe-target-health \
  --target-group-arn <ARN> \
  --region us-west-2
```

## Troubleshooting

### Common Issues

1. **ECS Tasks Not Starting**
   - Check CloudWatch logs for errors
   - Verify IAM role permissions
   - Check Secrets Manager access

2. **Target Group Unhealthy**
   - Verify security group rules
   - Check health check configuration
   - Review application logs

3. **Redis Connection Failed**
   - Verify security group allows port 6379
   - Check Redis endpoint in environment variables
   - Ensure Redis is in same VPC

4. **Cannot Generate Tokens**
   - Verify Secrets Manager permissions
   - Check secret ARNs are correct
   - Ensure secrets exist in us-west-2

See `LIVEKIT_TESTING.md` for detailed troubleshooting procedures.

## Cost Optimization

### Current Configuration
- ECS Fargate: 1 vCPU, 2GB RAM (~$1.50/day)
- ElastiCache: cache.t3.micro (~$0.50/day)
- NAT Gateways: 2 for HA (~$2.00/day)
- Load Balancers: ALB + NLB (~$1.50/day)
- **Total**: ~$5.50/day

### Optimization Tips
- Use Fargate Spot for non-critical workloads
- Reduce NAT Gateways to 1 (lower HA)
- Use VPC endpoints to reduce NAT costs
- Enable auto-scaling to match demand

## Security

### Encryption
- ✅ Data at rest: AES-256 (DynamoDB, Redis)
- ✅ Data in transit: TLS 1.3
- ✅ Secrets: AWS Secrets Manager
- ✅ Keys: AWS KMS

### Network Security
- ✅ ECS tasks in private subnets
- ✅ Redis in private subnets
- ✅ Security groups with least privilege
- ✅ No public IPs on ECS tasks

### IAM Security
- ✅ Least privilege IAM roles
- ✅ No hardcoded credentials
- ✅ Secrets Manager for sensitive data

## Breaking Barriers UK 2026 Compliance

✅ **Region**: All resources in us-west-2
✅ **Services**: Only permitted services (ECS, ElastiCache, ALB, NLB)
✅ **Encryption**: Enabled for all data
✅ **Instance Types**: cache.t3.micro (allowed)
✅ **Open Source**: LiveKit is open-source

## Next Steps

1. **Task 2.1**: Set up LiveKit Agent environment
2. **Task 2.2**: Build main agent with therapeutic context
3. **Task 2.3**: Integrate AgentCore memory loading
4. **Task 2.4**: Implement conversation tracking

## Resources

- [LiveKit Documentation](https://docs.livekit.io/)
- [LiveKit Agents Framework](https://docs.livekit.io/agents/)
- [AWS Bedrock Plugin](https://docs.livekit.io/agents/models/llm/plugins/aws/)
- [AWS Blog: Nova Sonic + LiveKit](https://aws.amazon.com/blogs/machine-learning/build-real-time-conversational-ai-experiences-using-amazon-nova-sonic-and-livekit/)

## Support

For issues or questions:
1. Check `LIVEKIT_TESTING.md` for troubleshooting
2. Review CloudWatch logs
3. Consult team documentation
4. Contact Environment Leads (see Breaking Barriers UK 2026 rules)

---

🏆 **Breaking Barriers UK 2026 Compliant**

**Time Saved**: ~20-25 hours of custom audio infrastructure development
**Status**: ✅ Infrastructure Complete, Ready for Agent Integration
