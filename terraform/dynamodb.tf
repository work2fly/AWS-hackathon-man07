# AI Therapy Platform - DynamoDB Resources
# Breaking Barriers UK 2026 compliant DynamoDB configuration

# KMS Key for DynamoDB encryption
resource "aws_kms_key" "main" {
  description             = "KMS key for AI Therapy Platform encryption"
  deletion_window_in_days = 7 # Short window for hackathon
  enable_key_rotation     = true
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-kms-key"
  })
}

resource "aws_kms_alias" "main" {
  name          = "alias/${local.name_prefix}-key"
  target_key_id = aws_kms_key.main.key_id
}

# Users Table
resource "aws_dynamodb_table" "users" {
  name           = "${local.name_prefix}-users"
  billing_mode   = var.dynamodb_billing_mode
  hash_key       = "userId"
  
  attribute {
    name = "userId"
    type = "S"
  }
  
  attribute {
    name = "email"
    type = "S"
  }
  
  # GSI for email-based queries
  global_secondary_index {
    name     = "EmailIndex"
    hash_key = "email"
    
    projection_type = "ALL"
  }
  
  # Enable encryption at rest
  server_side_encryption {
    enabled     = var.enable_encryption
    kms_key_arn = var.enable_encryption ? aws_kms_key.main.arn : null
  }
  
  # Enable point-in-time recovery
  point_in_time_recovery {
    enabled = var.dynamodb_point_in_time_recovery
  }
  
  # Deletion protection
  deletion_protection_enabled = var.enable_deletion_protection
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-users-table"
  })
}

# Sessions Table
resource "aws_dynamodb_table" "sessions" {
  name           = "${local.name_prefix}-sessions"
  billing_mode   = var.dynamodb_billing_mode
  hash_key       = "sessionId"
  range_key      = "timestamp"
  
  attribute {
    name = "sessionId"
    type = "S"
  }
  
  attribute {
    name = "timestamp"
    type = "S"
  }
  
  attribute {
    name = "clientId"
    type = "S"
  }
  
  # GSI for client-based queries
  global_secondary_index {
    name     = "ClientIndex"
    hash_key = "clientId"
    range_key = "timestamp"
    
    projection_type = "ALL"
  }
  
  # Enable encryption at rest
  server_side_encryption {
    enabled     = var.enable_encryption
    kms_key_arn = var.enable_encryption ? aws_kms_key.main.arn : null
  }
  
  # Enable point-in-time recovery
  point_in_time_recovery {
    enabled = var.dynamodb_point_in_time_recovery
  }
  
  # Deletion protection
  deletion_protection_enabled = var.enable_deletion_protection
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-sessions-table"
  })
}

# Red Flags Table
resource "aws_dynamodb_table" "redflags" {
  name           = "${local.name_prefix}-redflags"
  billing_mode   = var.dynamodb_billing_mode
  hash_key       = "sessionId"
  range_key      = "flagId"
  
  attribute {
    name = "sessionId"
    type = "S"
  }
  
  attribute {
    name = "flagId"
    type = "S"
  }
  
  attribute {
    name = "severity"
    type = "S"
  }
  
  attribute {
    name = "detectedAt"
    type = "S"
  }
  
  # GSI for severity-based queries
  global_secondary_index {
    name     = "SeverityIndex"
    hash_key = "severity"
    range_key = "detectedAt"
    
    projection_type = "ALL"
  }
  
  # Enable encryption at rest
  server_side_encryption {
    enabled     = var.enable_encryption
    kms_key_arn = var.enable_encryption ? aws_kms_key.main.arn : null
  }
  
  # Enable point-in-time recovery
  point_in_time_recovery {
    enabled = var.dynamodb_point_in_time_recovery
  }
  
  # Deletion protection
  deletion_protection_enabled = var.enable_deletion_protection
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-redflags-table"
  })
}

# Notifications Table
resource "aws_dynamodb_table" "notifications" {
  name           = "${local.name_prefix}-notifications"
  billing_mode   = var.dynamodb_billing_mode
  hash_key       = "recipientId"
  range_key      = "timestamp"
  
  attribute {
    name = "recipientId"
    type = "S"
  }
  
  attribute {
    name = "timestamp"
    type = "S"
  }
  
  attribute {
    name = "priority"
    type = "S"
  }
  
  # GSI for priority-based queries
  global_secondary_index {
    name     = "PriorityIndex"
    hash_key = "priority"
    range_key = "timestamp"
    
    projection_type = "ALL"
  }
  
  # Enable encryption at rest
  server_side_encryption {
    enabled     = var.enable_encryption
    kms_key_arn = var.enable_encryption ? aws_kms_key.main.arn : null
  }
  
  # Enable point-in-time recovery
  point_in_time_recovery {
    enabled = var.dynamodb_point_in_time_recovery
  }
  
  # Deletion protection
  deletion_protection_enabled = var.enable_deletion_protection
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-notifications-table"
  })
}

# WebSocket Connections Table
resource "aws_dynamodb_table" "websocket_connections" {
  name           = "${local.name_prefix}-websocket-connections"
  billing_mode   = var.dynamodb_billing_mode
  hash_key       = "connectionId"
  
  attribute {
    name = "connectionId"
    type = "S"
  }
  
  attribute {
    name = "userId"
    type = "S"
  }
  
  attribute {
    name = "sessionId"
    type = "S"
  }
  
  # GSI for user-based queries
  global_secondary_index {
    name     = "UserIndex"
    hash_key = "userId"
    
    projection_type = "ALL"
  }
  
  # GSI for session-based queries
  global_secondary_index {
    name     = "SessionIndex"
    hash_key = "sessionId"
    
    projection_type = "ALL"
  }
  
  # TTL for automatic cleanup of stale connections
  ttl {
    attribute_name = "ttl"
    enabled        = true
  }
  
  # Enable encryption at rest
  server_side_encryption {
    enabled     = var.enable_encryption
    kms_key_arn = var.enable_encryption ? aws_kms_key.main.arn : null
  }
  
  # Enable point-in-time recovery
  point_in_time_recovery {
    enabled = var.dynamodb_point_in_time_recovery
  }
  
  # Deletion protection
  deletion_protection_enabled = var.enable_deletion_protection
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-websocket-connections-table"
  })
}

# API Keys Table
resource "aws_dynamodb_table" "api_keys" {
  name           = "${local.name_prefix}-api-keys"
  billing_mode   = var.dynamodb_billing_mode
  hash_key       = "keyId"
  
  attribute {
    name = "keyId"
    type = "S"
  }
  
  attribute {
    name = "userId"
    type = "S"
  }
  
  # GSI for user-based queries
  global_secondary_index {
    name     = "UserIndex"
    hash_key = "userId"
    
    projection_type = "ALL"
  }
  
  # Enable encryption at rest
  server_side_encryption {
    enabled     = var.enable_encryption
    kms_key_arn = var.enable_encryption ? aws_kms_key.main.arn : null
  }
  
  # Enable point-in-time recovery
  point_in_time_recovery {
    enabled = var.dynamodb_point_in_time_recovery
  }
  
  # Deletion protection
  deletion_protection_enabled = var.enable_deletion_protection
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-api-keys-table"
  })
}

# Rate Limits Table
resource "aws_dynamodb_table" "rate_limits" {
  name           = "${local.name_prefix}-rate-limits"
  billing_mode   = var.dynamodb_billing_mode
  hash_key       = "limit_key"
  
  attribute {
    name = "limit_key"
    type = "S"
  }
  
  # TTL for automatic cleanup of expired rate limit records
  ttl {
    attribute_name = "ttl"
    enabled        = true
  }
  
  # Enable encryption at rest
  server_side_encryption {
    enabled     = var.enable_encryption
    kms_key_arn = var.enable_encryption ? aws_kms_key.main.arn : null
  }
  
  # Enable point-in-time recovery
  point_in_time_recovery {
    enabled = var.dynamodb_point_in_time_recovery
  }
  
  # Deletion protection
  deletion_protection_enabled = var.enable_deletion_protection
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-rate-limits-table"
  })
}
