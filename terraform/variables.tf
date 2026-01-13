# AI Therapy Platform - Terraform Variables
# Breaking Barriers UK 2026 compliant configuration

variable "aws_region" {
  description = "AWS region for deployment (Breaking Barriers UK 2026: us-west-2 only)"
  type        = string
  default     = "us-west-2"
  
  validation {
    condition = contains(["us-west-2", "us-east-1"], var.aws_region)
    error_message = "🏆 Breaking Barriers UK 2026: Only us-west-2 and us-east-1 regions are permitted."
  }
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
  
  validation {
    condition = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "ai-therapy-platform"
}

# DynamoDB Configuration
variable "dynamodb_billing_mode" {
  description = "DynamoDB billing mode"
  type        = string
  default     = "PAY_PER_REQUEST"
}

variable "dynamodb_point_in_time_recovery" {
  description = "Enable DynamoDB point-in-time recovery"
  type        = bool
  default     = true
}

# Lambda Configuration
variable "lambda_runtime" {
  description = "Lambda runtime version"
  type        = string
  default     = "python3.11"
}

variable "lambda_timeout" {
  description = "Lambda function timeout in seconds"
  type        = number
  default     = 30
}

variable "lambda_memory_size" {
  description = "Lambda function memory size in MB"
  type        = number
  default     = 256
}

# API Gateway Configuration
variable "api_gateway_stage_name" {
  description = "API Gateway stage name"
  type        = string
  default     = "dev"
}

# Cognito Configuration
variable "cognito_password_policy" {
  description = "Cognito password policy configuration"
  type = object({
    minimum_length    = number
    require_lowercase = bool
    require_numbers   = bool
    require_symbols   = bool
    require_uppercase = bool
  })
  default = {
    minimum_length    = 8
    require_lowercase = true
    require_numbers   = true
    require_symbols   = true
    require_uppercase = true
  }
}

variable "cognito_mfa_configuration" {
  description = "Cognito MFA configuration"
  type        = string
  default     = "OPTIONAL"
  
  validation {
    condition = contains(["OFF", "ON", "OPTIONAL"], var.cognito_mfa_configuration)
    error_message = "MFA configuration must be OFF, ON, or OPTIONAL."
  }
}

# Security Configuration
variable "enable_encryption" {
  description = "Enable encryption for all resources"
  type        = bool
  default     = true
}

variable "enable_deletion_protection" {
  description = "Enable deletion protection for critical resources"
  type        = bool
  default     = false # Set to false for hackathon to allow easy cleanup
}

# Monitoring Configuration
variable "enable_detailed_monitoring" {
  description = "Enable detailed CloudWatch monitoring"
  type        = bool
  default     = true
}

variable "log_retention_days" {
  description = "CloudWatch log retention period in days"
  type        = number
  default     = 7 # Short retention for hackathon
}

# Bedrock Configuration (Breaking Barriers UK 2026 compliant)
variable "bedrock_model_id" {
  description = "Bedrock model ID (Breaking Barriers UK 2026 compliant)"
  type        = string
  default     = "anthropic.claude-3-5-sonnet-20241022-v2:0"
  
  validation {
    condition = can(regex("^(anthropic\\.|amazon\\.|meta\\.|mistral\\.|stability\\.)", var.bedrock_model_id))
    error_message = "🏆 Breaking Barriers UK 2026: Only permitted Bedrock models are allowed."
  }
}

# Rate Limiting Configuration
variable "api_throttle_rate_limit" {
  description = "API Gateway throttle rate limit (requests per second)"
  type        = number
  default     = 100
}

variable "api_throttle_burst_limit" {
  description = "API Gateway throttle burst limit"
  type        = number
  default     = 200
}