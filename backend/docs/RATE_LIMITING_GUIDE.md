# Rate Limiting and Abuse Prevention Guide

🏆 Breaking Barriers UK 2026 compliant

## Overview

The AI Therapy Platform implements comprehensive rate limiting and abuse prevention to protect the system from excessive requests, brute force attacks, and malicious behavior. The system uses DynamoDB for distributed rate limit tracking and supports multiple limiting strategies.

## Architecture

```
┌─────────────────┐
│  API Request    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Rate Limiter Middleware        │
│  - Check if blocked             │
│  - Check rate limits            │
│  - Increment counters           │
│  - Detect abuse patterns        │
└────────┬────────────────────────┘
         │
         ├─── Blocked? ──► 429 Response
         │
         ├─── Limit Exceeded? ──► 429 Response
         │
         ▼
┌─────────────────────────────────┐
│  Process Request                │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  DynamoDB Rate Limits Table     │
│  - Request counters             │
│  - Block records                │
│  - Abuse counters               │
└─────────────────────────────────┘
```

## Rate Limit Configurations

### Default Limits

| Endpoint Type | Requests | Time Window | Use Case |
|--------------|----------|-------------|----------|
| Default | 100 | 60 seconds | General API endpoints |
| Authentication | 10 | 60 seconds | Login, registration |
| Chat | 30 | 60 seconds | AI chat messages |
| API Key | 1000 | 60 seconds | Programmatic access |

### Abuse Detection Thresholds

| Pattern | Threshold | Action | Block Duration |
|---------|-----------|--------|----------------|
| Rapid Requests | 50 in 10 seconds | Block IP | 1 hour |
| Failed Auth | 5 attempts | Block IP | 1 hour |
| Invalid Requests | 20 requests | Block IP | 1 hour |

## Implementation

### Using the Rate Limiter Decorator

The simplest way to add rate limiting to a Lambda handler:

```python
from security.rate_limiter import rate_limit_handler

@rate_limit_handler('chat')
def lambda_handler(event, context):
    """
    Handler with automatic rate limiting for chat endpoints
    """
    # Your handler code here
    return {
        'statusCode': 200,
        'body': {'message': 'Success'}
    }
```

### Manual Rate Limit Checking

For more control over rate limiting:

```python
from security.rate_limiter import RateLimiter

def lambda_handler(event, context):
    rate_limiter = RateLimiter()
    
    # Extract identifier (IP or API key)
    identifier = event['requestContext']['identity']['sourceIp']
    user_id = event['requestContext']['authorizer']['claims']['sub']
    
    # Check rate limit
    allowed, info = rate_limiter.check_rate_limit(
        identifier=identifier,
        limit_type='chat',
        user_id=user_id
    )
    
    if not allowed:
        return {
            'statusCode': 429,
            'headers': {
                'Retry-After': str(info['retry_after'])
            },
            'body': {
                'error': 'Rate limit exceeded',
                'message': info['message']
            }
        }
    
    # Process request
    # ...
    
    return {
        'statusCode': 200,
        'headers': {
            'X-RateLimit-Limit': str(info['limit']),
            'X-RateLimit-Remaining': str(info['remaining']),
            'X-RateLimit-Reset': str(info['reset_at'])
        },
        'body': {'message': 'Success'}
    }
```

### Recording Abuse Patterns

Track failed authentication attempts:

```python
from security.rate_limiter import RateLimiter

def login_handler(event, context):
    rate_limiter = RateLimiter()
    identifier = event['requestContext']['identity']['sourceIp']
    
    # Attempt authentication
    if not authenticate_user(username, password):
        # Record failed attempt
        rate_limiter.record_failed_auth(identifier)
        
        return {
            'statusCode': 401,
            'body': {'error': 'Invalid credentials'}
        }
    
    # Successful login
    return {
        'statusCode': 200,
        'body': {'token': 'jwt_token_here'}
    }
```

Track invalid requests:

```python
from security.rate_limiter import RateLimiter

def api_handler(event, context):
    rate_limiter = RateLimiter()
    identifier = event['requestContext']['identity']['sourceIp']
    
    # Validate request
    if not validate_request(event):
        # Record invalid request
        rate_limiter.record_invalid_request(identifier)
        
        return {
            'statusCode': 400,
            'body': {'error': 'Invalid request'}
        }
    
    # Process valid request
    # ...
```

## DynamoDB Schema

### Rate Limits Table

```python
{
    'limit_key': 'rate:chat:abc123:12345',  # PK: Composite key
    'identifier': '[ip_address]',            # IP or API key
    'limit_type': 'chat',                    # Type of limit
    'request_count': 15,                     # Current count
    'window_start': 1705234567,              # Window start timestamp
    'last_request': 1705234580,              # Last request timestamp
    'ttl': 1705238167                        # Auto-expire after window
}
```

### Block Records

```python
{
    'limit_key': 'block:[ip_address]',       # PK: Block key
    'identifier': '[ip_address]',            # Blocked identifier
    'blocked': True,                         # Block status
    'reason': 'excessive_failed_auth',       # Block reason
    'blocked_at': 1705234567,                # Block timestamp
    'block_until': 1705238167,               # Block expiry
    'ttl': 1705241767                        # Auto-cleanup
}
```

### Abuse Counters

```python
{
    'limit_key': 'abuse:[ip_address]:failed_auth',  # PK: Counter key
    'identifier': '[ip_address]',                   # Identifier
    'counter_type': 'failed_auth',                  # Counter type
    'abuse_count': 3,                               # Current count
    'last_abuse': 1705234567,                       # Last incident
    'ttl': 1705235167                               # Expire after 10 min
}
```

## Response Headers

Rate limit information is included in response headers:

```
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 25
X-RateLimit-Reset: 1705234620
```

When rate limit is exceeded:

```
HTTP/1.1 429 Too Many Requests
Retry-After: 45
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1705234620

{
    "error": "Rate limit exceeded",
    "message": "Rate limit exceeded. Try again in 45 seconds.",
    "retry_after": 45
}
```

## Admin Functions

### Unblock an Identifier

```python
from security.rate_limiter import RateLimiter

def admin_unblock_handler(event, context):
    rate_limiter = RateLimiter()
    
    # Extract identifier from request
    identifier = event['body']['identifier']
    
    # Unblock
    success = rate_limiter.unblock_identifier(identifier)
    
    return {
        'statusCode': 200 if success else 500,
        'body': {
            'success': success,
            'message': f'Identifier {identifier} unblocked' if success else 'Failed to unblock'
        }
    }
```

### Get Rate Limit Status

```python
from security.rate_limiter import RateLimiter

def admin_status_handler(event, context):
    rate_limiter = RateLimiter()
    
    identifier = event['queryStringParameters']['identifier']
    limit_type = event['queryStringParameters'].get('type', 'default')
    
    info = rate_limiter.get_rate_limit_info(identifier, limit_type)
    
    return {
        'statusCode': 200,
        'body': info
    }
```

## Customizing Rate Limits

### Modify Limit Configurations

Edit the `RateLimiter` class initialization:

```python
class RateLimiter:
    def __init__(self, table_name: str = None):
        # ...
        
        # Custom rate limit configurations
        self.limits = {
            'default': {'requests': 100, 'window': 60},
            'auth': {'requests': 10, 'window': 60},
            'chat': {'requests': 50, 'window': 60},  # Increased from 30
            'api_key': {'requests': 1000, 'window': 60},
            'admin': {'requests': 500, 'window': 60},  # New limit type
        }
```

### Modify Abuse Thresholds

```python
class RateLimiter:
    def __init__(self, table_name: str = None):
        # ...
        
        # Custom abuse detection thresholds
        self.abuse_thresholds = {
            'rapid_requests': 100,     # Increased from 50
            'failed_auth': 3,          # Decreased from 5
            'invalid_requests': 20,
            'block_duration': 7200,    # 2 hours instead of 1
        }
```

## Testing

### Test Rate Limiting

```python
import pytest
from security.rate_limiter import RateLimiter

def test_rate_limit_enforcement():
    rate_limiter = RateLimiter()
    identifier = '[test_ip]'
    
    # Make requests up to limit
    for i in range(30):
        allowed, info = rate_limiter.check_rate_limit(
            identifier=identifier,
            limit_type='chat'
        )
        assert allowed is True
        assert info['remaining'] == 30 - i - 1
    
    # Next request should be blocked
    allowed, info = rate_limiter.check_rate_limit(
        identifier=identifier,
        limit_type='chat'
    )
    assert allowed is False
    assert info['reason'] == 'rate_limit_exceeded'
```

### Test Abuse Detection

```python
def test_failed_auth_blocking():
    rate_limiter = RateLimiter()
    identifier = '[test_ip]'
    
    # Record failed auth attempts
    for i in range(5):
        rate_limiter.record_failed_auth(identifier)
    
    # Should be blocked now
    assert rate_limiter._is_blocked(identifier) is True
    
    # Requests should be rejected
    allowed, info = rate_limiter.check_rate_limit(
        identifier=identifier,
        limit_type='auth'
    )
    assert allowed is False
    assert info['reason'] == 'blocked'
```

## Monitoring

### CloudWatch Metrics

Monitor rate limiting effectiveness:

```python
import boto3

cloudwatch = boto3.client('cloudwatch', region_name='us-west-2')

def publish_rate_limit_metrics(identifier: str, limit_type: str, blocked: bool):
    """Publish rate limit metrics to CloudWatch"""
    cloudwatch.put_metric_data(
        Namespace='AITherapyPlatform/RateLimiting',
        MetricData=[
            {
                'MetricName': 'RateLimitExceeded',
                'Value': 1 if blocked else 0,
                'Unit': 'Count',
                'Dimensions': [
                    {'Name': 'LimitType', 'Value': limit_type}
                ]
            }
        ]
    )
```

### CloudWatch Alarms

Create alarms for excessive blocking:

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name high-rate-limit-blocks \
  --alarm-description "Alert when rate limit blocks are high" \
  --metric-name RateLimitExceeded \
  --namespace AITherapyPlatform/RateLimiting \
  --statistic Sum \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 100 \
  --comparison-operator GreaterThanThreshold
```

## Best Practices

1. **Use appropriate limit types**: Choose the right limit type for each endpoint
2. **Monitor abuse patterns**: Regularly review blocked IPs and abuse counters
3. **Adjust thresholds**: Fine-tune limits based on actual usage patterns
4. **Implement graceful degradation**: Handle rate limit errors gracefully in clients
5. **Provide clear error messages**: Help users understand why they're blocked
6. **Use exponential backoff**: Implement retry logic with exponential backoff
7. **Whitelist trusted IPs**: Consider whitelisting known good actors
8. **Log all blocks**: Maintain audit trail of all blocking actions

## Security Considerations

1. **IP spoofing**: Consider using additional identifiers beyond IP address
2. **Distributed attacks**: Monitor for coordinated attacks from multiple IPs
3. **API key rotation**: Encourage regular API key rotation
4. **False positives**: Provide mechanism for users to appeal blocks
5. **DDoS protection**: Combine with AWS WAF for comprehensive protection

## Troubleshooting

### High False Positive Rate

If legitimate users are being blocked:

1. Increase rate limit thresholds
2. Adjust abuse detection sensitivity
3. Review block reasons in DynamoDB
4. Consider implementing user-based limits instead of IP-based

### Rate Limiter Not Working

Check:

1. DynamoDB table exists and is accessible
2. Lambda has correct IAM permissions
3. Environment variables are set correctly
4. TTL is enabled on the table

### Performance Issues

If rate limiting is slow:

1. Enable DynamoDB auto-scaling
2. Use on-demand billing mode
3. Optimize query patterns
4. Consider caching rate limit status

## Related Documentation

- [API Security Guide](./API_SECURITY_GUIDE.md)
- [Deployment Guide](./DEPLOYMENT_GUIDE.md)
- [Monitoring Guide](./MONITORING_GUIDE.md)
