# AI Therapy Platform - Cognito Resources
# Breaking Barriers UK 2026 compliant authentication

# Cognito User Pool
resource "aws_cognito_user_pool" "main" {
  name = "${local.name_prefix}-user-pool"
  
  # User attributes
  alias_attributes = ["email"]
  auto_verified_attributes = ["email"]
  
  # Password policy
  password_policy {
    minimum_length    = var.cognito_password_policy.minimum_length
    require_lowercase = var.cognito_password_policy.require_lowercase
    require_numbers   = var.cognito_password_policy.require_numbers
    require_symbols   = var.cognito_password_policy.require_symbols
    require_uppercase = var.cognito_password_policy.require_uppercase
  }
  
  # MFA configuration
  mfa_configuration = var.cognito_mfa_configuration
  
  # Software token MFA
  software_token_mfa_configuration {
    enabled = var.cognito_mfa_configuration != "OFF"
  }
  
  # Account recovery
  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }
  }
  
  # User pool add-ons
  user_pool_add_ons {
    advanced_security_mode = "ENFORCED"
  }
  
  # Email configuration
  email_configuration {
    email_sending_account = "COGNITO_DEFAULT"
  }
  
  # Verification message template
  verification_message_template {
    default_email_option = "CONFIRM_WITH_CODE"
    email_subject        = "AI Therapy Platform - Verify your email"
    email_message        = "Your verification code is {####}"
  }
  
  # User attribute update settings
  user_attribute_update_settings {
    attributes_require_verification_before_update = ["email"]
  }
  
  # Schema for custom attributes
  schema {
    attribute_data_type = "String"
    name               = "role"
    required           = false
    mutable            = true
    
    string_attribute_constraints {
      min_length = 1
      max_length = 20
    }
  }
  
  schema {
    attribute_data_type = "String"
    name               = "language_preference"
    required           = false
    mutable            = true
    
    string_attribute_constraints {
      min_length = 2
      max_length = 10
    }
  }
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-user-pool"
  })
}

# Cognito User Pool Client
resource "aws_cognito_user_pool_client" "main" {
  name         = "${local.name_prefix}-client"
  user_pool_id = aws_cognito_user_pool.main.id
  
  # Client settings
  generate_secret                      = true
  allowed_oauth_flows_user_pool_client = true
  
  # OAuth settings
  allowed_oauth_flows = ["code", "implicit"]
  allowed_oauth_scopes = ["email", "openid", "profile"]
  
  callback_urls = [
    "http://localhost:3000/callback",
    "https://${local.name_prefix}.auth.${local.region}.amazoncognito.com/oauth2/idpresponse"
  ]
  
  logout_urls = [
    "http://localhost:3000/logout",
    "https://${local.name_prefix}.auth.${local.region}.amazoncognito.com/logout"
  ]
  
  # Supported identity providers
  supported_identity_providers = ["COGNITO"]
  
  # Token validity
  access_token_validity  = 1  # 1 hour
  id_token_validity     = 1  # 1 hour
  refresh_token_validity = 30 # 30 days
  
  token_validity_units {
    access_token  = "hours"
    id_token      = "hours"
    refresh_token = "days"
  }
  
  # Explicit auth flows
  explicit_auth_flows = [
    "ALLOW_ADMIN_USER_PASSWORD_AUTH",
    "ALLOW_CUSTOM_AUTH",
    "ALLOW_USER_PASSWORD_AUTH",
    "ALLOW_USER_SRP_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH"
  ]
  
  # Prevent user existence errors
  prevent_user_existence_errors = "ENABLED"
  
  # Read and write attributes
  read_attributes = [
    "email",
    "email_verified",
    "custom:role",
    "custom:language_preference"
  ]
  
  write_attributes = [
    "email",
    "custom:role",
    "custom:language_preference"
  ]
}

# Cognito User Pool Domain
resource "aws_cognito_user_pool_domain" "main" {
  domain       = "${local.name_prefix}-auth-${random_string.domain_suffix.result}"
  user_pool_id = aws_cognito_user_pool.main.id
}

# Random string for unique domain
resource "random_string" "domain_suffix" {
  length  = 8
  special = false
  upper   = false
}

# Cognito User Groups for role-based access control
resource "aws_cognito_user_group" "clients" {
  name         = "clients"
  user_pool_id = aws_cognito_user_pool.main.id
  description  = "Client users who receive therapy sessions"
  precedence   = 3
}

resource "aws_cognito_user_group" "therapists" {
  name         = "therapists"
  user_pool_id = aws_cognito_user_pool.main.id
  description  = "Therapist users who monitor sessions and receive red flag notifications"
  precedence   = 2
}

resource "aws_cognito_user_group" "admins" {
  name         = "admins"
  user_pool_id = aws_cognito_user_pool.main.id
  description  = "Admin users with full system management capabilities"
  precedence   = 1
}

# Lambda function for Cognito triggers
resource "aws_lambda_function" "cognito_triggers" {
  filename         = "cognito_triggers.zip"
  function_name    = "${local.name_prefix}-cognito-triggers"
  role            = aws_iam_role.lambda_execution_role.arn
  handler         = "cognito_triggers.lambda_handler"
  runtime         = var.lambda_runtime
  timeout         = var.lambda_timeout
  memory_size     = var.lambda_memory_size
  
  environment {
    variables = {
      USERS_TABLE_NAME = aws_dynamodb_table.users.name
      AWS_REGION      = local.region
    }
  }
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-cognito-triggers"
  })
}

# Lambda permission for Cognito to invoke the function
resource "aws_lambda_permission" "cognito_triggers" {
  statement_id  = "AllowCognitoInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.cognito_triggers.function_name
  principal     = "cognito-idp.amazonaws.com"
  source_arn    = aws_cognito_user_pool.main.arn
}

# Cognito User Pool Lambda Config (triggers)
resource "aws_cognito_user_pool_lambda_config" "main" {
  user_pool_id = aws_cognito_user_pool.main.id
  
  pre_sign_up                    = aws_lambda_function.cognito_triggers.arn
  post_confirmation             = aws_lambda_function.cognito_triggers.arn
  pre_authentication            = aws_lambda_function.cognito_triggers.arn
  post_authentication           = aws_lambda_function.cognito_triggers.arn
  custom_message                = aws_lambda_function.cognito_triggers.arn
}