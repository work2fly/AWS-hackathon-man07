# LiveKit Infrastructure Quick Reference
🏆 Breaking Barriers UK 2026 Hackathon

## Essential Commands

### Get LiveKit Server URL
```bash
cd terraform
terraform output -json livekit_connection_info | jq -r '.server_url'
```

### Get API Credentials
```bash
# API Key
aws secretsmanager get-secret-value \
  --secret-id ai-therapy-platform-dev-livekit-key-only \
  --region us-west-2 --query SecretString --output text

# API Secret
aws secretsmanager get-secret-value \
  --secret-id ai-therapy-platform-dev-livekit-api-secret \
  --region us-west-2 --query SecretString --output text
```

### Check Service Health
```bash
# ECS Service Status
aws ecs describe-services \
  --cluster ai-therapy-platform-dev-livekit-cluster \
  --services ai-therapy-platform-dev-livekit-service \
  --region us-west-2 \
  --query 'services[0].[status,runningCount,desiredCount]'

# View Logs
aws logs tail /ecs/ai-therapy-platform-dev-livekit --follow --region us-west-2
```

### Test Infrastructure
```bash
cd terraform/scripts
./test-livekit-connectivity.sh
python3 test-livekit-token.py
```

## Key Resources

### URLs
- **Server URL**: `ws://<ALB-DNS>:7880`
- **Secure URL**: `wss://<ALB-DNS>:7881`

### Ports
- **7880**: HTTP
- **7881**: HTTPS
- **50000-60000**: WebRTC

### DynamoDB Tables
- **LiveKitRooms**: `ai-therapy-platform-dev-livekit-rooms`

### CloudWatch Logs
- **Log Group**: `/ecs/ai-therapy-platform-dev-livekit`

## Token Generation (Python)

```python
from livekit import api
from datetime import timedelta

token = api.AccessToken(api_key, api_secret)
token.with_identity(user_id)
token.with_name(user_name)
token.with_grants(api.VideoGrants(
    room_join=True,
    room=room_name,
    can_publish=True,
    can_subscribe=True,
))
token.with_ttl(timedelta(hours=1))
jwt_token = token.to_jwt()
```

## Troubleshooting

### Tasks Not Starting
```bash
aws logs tail /ecs/ai-therapy-platform-dev-livekit --region us-west-2
```

### Target Group Unhealthy
```bash
aws elbv2 describe-target-health \
  --target-group-arn <ARN> --region us-west-2
```

### Cannot Access Secrets
Check IAM role: `ai-therapy-platform-dev-ecs-task-execution-role`

## Documentation
- **Deployment**: `terraform/LIVEKIT_DEPLOYMENT.md`
- **Testing**: `terraform/LIVEKIT_TESTING.md`
- **Summary**: `LIVEKIT_INFRASTRUCTURE_SUMMARY.md`

---

🏆 Breaking Barriers UK 2026 Compliant
