# AI Therapy Platform - Terraform Outputs
# Breaking Barriers UK 2026 compliant outputs

# General Information
output "account_id" {
  description = "AWS Account ID"
  value       = local.account_id
}

output "region" {
  description = "AWS Region"
  value       = local.region
}

output "environment" {
  description = "Environment name"
  value       = var.environment
}

# IAM Outputs
output "lambda_execution_role_arn" {
  description = "Lambda execution role ARN"
  value       = aws_iam_role.lambda_execution_role.arn
}

# DynamoDB Outputs
output "dynamodb_tables" {
  description = "DynamoDB table information"
  value = {
    users_table = {
      name = aws_dynamodb_table.users.name
      arn  = aws_dynamodb_table.users.arn
    }
    sessions_table = {
      name = aws_dynamodb_table.sessions.name
      arn  = aws_dynamodb_table.sessions.arn
    }
    redflags_table = {
      name = aws_dynamodb_table.redflags.name
      arn  = aws_dynamodb_table.redflags.arn
    }
    notifications_table = {
      name = aws_dynamodb_table.notifications.name
      arn  = aws_dynamodb_table.notifications.arn
    }
    livekit_rooms_table = {
      name = aws_dynamodb_table.livekit_rooms.name
      arn  = aws_dynamodb_table.livekit_rooms.arn
    }
  }
}

# Cognito Outputs
output "cognito_user_pool" {
  description = "Cognito User Pool information"
  value = {
    id       = aws_cognito_user_pool.main.id
    arn      = aws_cognito_user_pool.main.arn
    endpoint = aws_cognito_user_pool.main.endpoint
  }
}

output "cognito_user_pool_client" {
  description = "Cognito User Pool Client information"
  value = {
    id   = aws_cognito_user_pool_client.main.id
    name = aws_cognito_user_pool_client.main.name
  }
  sensitive = true
}

output "cognito_user_groups" {
  description = "Cognito User Groups information"
  value = {
    clients = {
      name = aws_cognito_user_group.clients.name
      precedence = aws_cognito_user_group.clients.precedence
    }
    therapists = {
      name = aws_cognito_user_group.therapists.name
      precedence = aws_cognito_user_group.therapists.precedence
    }
    admins = {
      name = aws_cognito_user_group.admins.name
      precedence = aws_cognito_user_group.admins.precedence
    }
  }
}

output "cognito_domain" {
  description = "Cognito User Pool Domain"
  value = {
    domain = aws_cognito_user_pool_domain.main.domain
    cloudfront_distribution_arn = aws_cognito_user_pool_domain.main.cloudfront_distribution_arn
  }
}

# API Gateway Outputs
output "api_gateway_websocket" {
  description = "API Gateway WebSocket information"
  value = {
    id               = aws_apigatewayv2_api.websocket.id
    api_endpoint     = aws_apigatewayv2_api.websocket.api_endpoint
    execution_arn    = aws_apigatewayv2_api.websocket.execution_arn
  }
}

output "api_gateway_rest" {
  description = "API Gateway REST API information"
  value = {
    id               = aws_api_gateway_rest_api.main.id
    execution_arn    = aws_api_gateway_rest_api.main.execution_arn
    invoke_url       = "https://${aws_api_gateway_rest_api.main.id}.execute-api.${local.region}.amazonaws.com/${var.api_gateway_stage_name}"
  }
}

# CloudWatch Outputs
output "cloudwatch_log_groups" {
  description = "CloudWatch log group information"
  value = {
    api_gateway = aws_cloudwatch_log_group.api_gateway.name
    lambda      = aws_cloudwatch_log_group.lambda.name
  }
}

# KMS Outputs
output "kms_key" {
  description = "KMS key information"
  value = {
    id  = aws_kms_key.main.id
    arn = aws_kms_key.main.arn
  }
}

# LiveKit Infrastructure Outputs
output "livekit_infrastructure" {
  description = "LiveKit infrastructure information"
  value = {
    alb_dns_name = aws_lb.livekit.dns_name
    nlb_dns_name = aws_lb.livekit_webrtc.dns_name
    ecs_cluster_name = aws_ecs_cluster.livekit.name
    ecs_service_name = aws_ecs_service.livekit.name
    redis_endpoint = aws_elasticache_cluster.livekit.cache_nodes[0].address
    redis_port = aws_elasticache_cluster.livekit.cache_nodes[0].port
  }
}

output "livekit_api_credentials" {
  description = "LiveKit API credentials (stored in Secrets Manager)"
  value = {
    api_key_secret_arn = aws_secretsmanager_secret.livekit_api_key.arn
    api_secret_secret_arn = aws_secretsmanager_secret.livekit_api_secret.arn
  }
  sensitive = true
}

output "livekit_connection_info" {
  description = "LiveKit connection information for clients"
  value = {
    server_url = "ws://${aws_lb.livekit.dns_name}:7880"
    server_url_secure = "wss://${aws_lb.livekit.dns_name}:7881"
  }
}

# VPC Outputs
output "vpc_info" {
  description = "VPC information"
  value = {
    vpc_id = aws_vpc.main.id
    public_subnet_ids = aws_subnet.public[*].id
    private_subnet_ids = aws_subnet.private[*].id
  }
}

# Environment Configuration for Applications
output "environment_config" {
  description = "Environment configuration for applications"
  value = {
    AWS_REGION                = local.region
    AWS_ACCOUNT_ID           = local.account_id
    LAMBDA_EXECUTION_ROLE_ARN = aws_iam_role.lambda_execution_role.arn
    
    # DynamoDB
    USERS_TABLE_NAME         = aws_dynamodb_table.users.name
    SESSIONS_TABLE_NAME      = aws_dynamodb_table.sessions.name
    REDFLAGS_TABLE_NAME      = aws_dynamodb_table.redflags.name
    NOTIFICATIONS_TABLE_NAME = aws_dynamodb_table.notifications.name
    LIVEKIT_ROOMS_TABLE_NAME = aws_dynamodb_table.livekit_rooms.name
    
    # Cognito
    COGNITO_USER_POOL_ID     = aws_cognito_user_pool.main.id
    COGNITO_CLIENT_ID        = aws_cognito_user_pool_client.main.id
    
    # API Gateway
    WEBSOCKET_API_ENDPOINT   = aws_apigatewayv2_api.websocket.api_endpoint
    REST_API_ENDPOINT        = "https://${aws_api_gateway_rest_api.main.id}.execute-api.${local.region}.amazonaws.com/${var.api_gateway_stage_name}"
    
    # LiveKit
    LIVEKIT_SERVER_URL       = "ws://${aws_lb.livekit.dns_name}:7880"
    LIVEKIT_API_KEY_SECRET   = aws_secretsmanager_secret.livekit_api_key.arn
    LIVEKIT_API_SECRET_SECRET = aws_secretsmanager_secret.livekit_api_secret.arn
    REDIS_ENDPOINT           = aws_elasticache_cluster.livekit.cache_nodes[0].address
    
    # Security
    KMS_KEY_ID               = aws_kms_key.main.id
    
    # Bedrock (Breaking Barriers UK 2026 compliant)
    BEDROCK_MODEL_ID         = var.bedrock_model_id
  }
  sensitive = true
}