---
inclusion: manual
---

# AWS Lambda Best Practices - Breaking Barriers UK 2026

## Purpose
Detailed guidance for AWS Lambda development to prevent common deployment errors and follow best practices during the hackathon.

## Environment Variables

### Reserved Environment Variables (NEVER SET MANUALLY)
AWS Lambda automatically provides these environment variables. Setting them manually in Terraform will cause `InvalidParameterValueException`:

```hcl
# ❌ WRONG - Do not set these in Terraform
environment {
  variables = {
    AWS_REGION = "us-west-2"  # RESERVED - causes deployment error
    AWS_DEFAULT_REGION = "us-west-2"  # RESERVED - causes deployment error
    AWS_EXECUTION_ENV = "AWS_Lambda_python3.9"  # RESERVED
    AWS_LAMBDA_FUNCTION_NAME = "my-function"  # RESERVED
    # ... other reserved variables
  }
}
```

```hcl
# ✅ CORRECT - Only set custom application variables
environment {
  variables = {
    USERS_TABLE_NAME = aws_dynamodb_table.users.name
    COGNITO_USER_POOL_ID = aws_cognito_user_pool.main.id
    API_BASE_URL = "https://api.example.com"
    LOG_LEVEL = "INFO"
  }
}
```

### Complete List of Reserved Variables
- `AWS_REGION` - The AWS region where the function is running
- `AWS_DEFAULT_REGION` - Same as AWS_REGION
- `AWS_EXECUTION_ENV` - The runtime identifier (e.g., AWS_Lambda_python3.9)
- `AWS_LAMBDA_FUNCTION_NAME` - The name of the function
- `AWS_LAMBDA_FUNCTION_MEMORY_SIZE` - The amount of memory allocated
- `AWS_LAMBDA_FUNCTION_VERSION` - The version of the function
- `AWS_LAMBDA_RUNTIME_API` - The runtime API endpoint
- `AWS_LAMBDA_LOG_GROUP_NAME` - CloudWatch log group name
- `AWS_LAMBDA_LOG_STREAM_NAME` - CloudWatch log stream name
- `_HANDLER` - The handler location configured on the function
- `TZ` - The timezone (UTC by default)
- `AWS_ACCESS_KEY_ID` - AWS access key (when using IAM roles)
- `AWS_SECRET_ACCESS_KEY` - AWS secret key (when using IAM roles)
- `AWS_SESSION_TOKEN` - AWS session token (when using IAM roles)

### Accessing Region in Code

```python
# ✅ CORRECT - Access region in Python
import os

# AWS Lambda automatically provides this
region = os.getenv('AWS_DEFAULT_REGION', 'us-west-2')
# or
region = os.getenv('AWS_REGION', 'us-west-2')

# Use in boto3 clients
import boto3
dynamodb = boto3.resource('dynamodb', region_name=region)
```

```javascript
// ✅ CORRECT - Access region in Node.js
const region = process.env.AWS_DEFAULT_REGION || 'us-west-2';
// or
const region = process.env.AWS_REGION || 'us-west-2';

// Use in AWS SDK
const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient({ region });
```

## Function Configuration Best Practices

### Memory and Timeout
```hcl
resource "aws_lambda_function" "example" {
  # Memory: 128MB to 10,240MB (in 1MB increments)
  memory_size = 512  # Start with 512MB, adjust based on testing
  
  # Timeout: 1 second to 15 minutes
  timeout = 30  # 30 seconds for most API functions
  
  # Runtime
  runtime = "python3.9"  # Use supported runtimes
}
```

### Package Size Limits
- **Deployment package**: 50MB (unzipped), 10MB (zipped) for console editing
- **Layers**: 250MB (unzipped) total across all layers
- **Temporary storage**: 512MB to 10,240MB in `/tmp`

### Dead Letter Queues
```hcl
resource "aws_lambda_function" "example" {
  # Configure DLQ for failed executions
  dead_letter_config {
    target_arn = aws_sqs_queue.dlq.arn
  }
}

resource "aws_sqs_queue" "dlq" {
  name = "${local.name_prefix}-lambda-dlq"
  
  # Retain messages for debugging
  message_retention_seconds = 1209600  # 14 days
}
```

### VPC Configuration (if needed)
```hcl
resource "aws_lambda_function" "example" {
  # Only if Lambda needs to access VPC resources
  vpc_config {
    subnet_ids         = var.private_subnet_ids
    security_group_ids = [aws_security_group.lambda.id]
  }
  
  # VPC Lambdas need more time to start
  timeout = 60
}
```

## Error Prevention Checklist

### Before Deployment
- [ ] No reserved environment variables in Terraform
- [ ] Function timeout appropriate for workload
- [ ] Memory size optimized (start with 512MB)
- [ ] IAM role has minimum required permissions
- [ ] Dead letter queue configured for critical functions
- [ ] CloudWatch logs retention period set
- [ ] Package size under limits

### Common Deployment Errors
1. **InvalidParameterValueException**: Reserved environment variables
   - **Fix**: Remove `AWS_REGION`, `AWS_DEFAULT_REGION`, etc. from Terraform
   
2. **ResourceConflictException**: Function already exists
   - **Fix**: Use `terraform import` or destroy/recreate
   
3. **InvalidZipFileException**: Corrupted deployment package
   - **Fix**: Rebuild Lambda package, check file permissions
   
4. **CodeStorageExceededException**: Package too large
   - **Fix**: Use Lambda layers, optimize dependencies

## Monitoring and Logging

### CloudWatch Integration
```hcl
# Log group with retention
resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${aws_lambda_function.example.function_name}"
  retention_in_days = 7  # Adjust based on needs
}

# Metric alarms
resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  alarm_name          = "${local.name_prefix}-lambda-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = "300"
  statistic           = "Sum"
  threshold           = "5"
  alarm_description   = "Lambda function error rate too high"
  
  dimensions = {
    FunctionName = aws_lambda_function.example.function_name
  }
}
```

### Structured Logging in Code
```python
import json
import logging

# Configure structured logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    # Log structured data
    logger.info(json.dumps({
        'event': 'function_start',
        'request_id': context.aws_request_id,
        'function_name': context.function_name,
        'remaining_time': context.get_remaining_time_in_millis()
    }))
    
    try:
        # Your function logic
        result = process_event(event)
        
        logger.info(json.dumps({
            'event': 'function_success',
            'request_id': context.aws_request_id
        }))
        
        return result
        
    except Exception as e:
        logger.error(json.dumps({
            'event': 'function_error',
            'request_id': context.aws_request_id,
            'error': str(e)
        }))
        raise
```

## Security Best Practices

### IAM Permissions
```hcl
# Principle of least privilege
resource "aws_iam_role_policy" "lambda_policy" {
  name = "${local.name_prefix}-lambda-policy"
  role = aws_iam_role.lambda_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem"
        ]
        Resource = aws_dynamodb_table.users.arn
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}
```

### Environment Variable Encryption
```hcl
resource "aws_lambda_function" "example" {
  # Encrypt environment variables at rest
  kms_key_arn = aws_kms_key.lambda.arn
  
  environment {
    variables = {
      # Sensitive data should use AWS Secrets Manager instead
      DATABASE_URL = "encrypted_value"
    }
  }
}
```

## Performance Optimization

### Cold Start Reduction
- Keep deployment packages small
- Minimize dependencies
- Use provisioned concurrency for critical functions
- Initialize connections outside handler function

### Memory vs Cost Optimization
```python
# Test different memory settings
# Higher memory = more CPU power = potentially faster execution = lower cost
# Monitor CloudWatch metrics to find optimal setting
```

## Breaking Barriers UK 2026 Compliance

### Region Restrictions
- Deploy only in `us-west-2` region
- Use `us-east-1` only for global services (CloudFront, Route 53)

### Service Integration
- Use only permitted AWS services from the approved list
- Integrate with Cognito for authentication
- Use DynamoDB for data storage
- Implement CloudWatch monitoring

### Cost Management
- Set appropriate memory sizes (don't over-provision)
- Use efficient runtimes (Python 3.9, Node.js 18.x)
- Monitor execution duration and optimize code
- Clean up unused functions and versions

## Troubleshooting Quick Reference

| Error | Cause | Solution |
|-------|-------|----------|
| InvalidParameterValueException | Reserved env var | Remove AWS_REGION from Terraform |
| ResourceConflictException | Function exists | Import existing or destroy/recreate |
| InvalidZipFileException | Bad package | Rebuild deployment package |
| CodeStorageExceededException | Package too large | Use layers, optimize dependencies |
| AccessDeniedException | IAM permissions | Add required permissions to role |
| SubnetNotFoundException | VPC config | Check subnet IDs and availability |

Remember: Always test Lambda functions locally before deployment and monitor CloudWatch logs for issues! 🏆 Breaking Barriers UK 2026 compliant