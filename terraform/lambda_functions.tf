# AI Therapy Platform - Lambda Functions
# Breaking Barriers UK 2026 compliant Lambda configuration

# Chat Handler Lambda Function
resource "aws_lambda_function" "chat_handler" {
  filename         = "chat_handler.zip"
  function_name    = "${local.name_prefix}-chat-handler"
  role            = aws_iam_role.lambda_execution_role.arn
  handler         = "chat_handler.lambda_handler"
  runtime         = var.lambda_runtime
  timeout         = 60 # Longer timeout for Bedrock API calls
  memory_size     = 512 # More memory for AI processing
  
  environment {
    variables = {
      SESSIONS_TABLE_NAME      = aws_dynamodb_table.sessions.name
      USERS_TABLE_NAME         = aws_dynamodb_table.users.name
      REDFLAGS_TABLE_NAME      = aws_dynamodb_table.redflags.name
      API_KEYS_TABLE_NAME      = aws_dynamodb_table.api_keys.name
      RATE_LIMITS_TABLE_NAME   = aws_dynamodb_table.rate_limits.name
      BEDROCK_MODEL_ID         = var.bedrock_model_id
      COGNITO_USER_POOL_ID     = aws_cognito_user_pool.main.id
    }
  }
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-chat-handler"
  })
}

# Lambda permission for API Gateway to invoke chat handler
resource "aws_lambda_permission" "chat_handler" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.chat_handler.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.main.execution_arn}/*/*"
}

# Session Analysis Lambda Function
resource "aws_lambda_function" "session_analysis" {
  filename         = "session_analysis.zip"
  function_name    = "${local.name_prefix}-session-analysis"
  role            = aws_iam_role.lambda_execution_role.arn
  handler         = "session_analysis.lambda_handler"
  runtime         = var.lambda_runtime
  timeout         = 60 # Longer timeout for analysis
  memory_size     = 512
  
  environment {
    variables = {
      SESSIONS_TABLE_NAME      = aws_dynamodb_table.sessions.name
      USERS_TABLE_NAME         = aws_dynamodb_table.users.name
      REDFLAGS_TABLE_NAME      = aws_dynamodb_table.redflags.name
      NOTIFICATIONS_TABLE_NAME = aws_dynamodb_table.notifications.name
      BEDROCK_MODEL_ID         = var.bedrock_model_id
    }
  }
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-session-analysis"
  })
}

# Lambda permission for API Gateway to invoke session analysis
resource "aws_lambda_permission" "session_analysis" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.session_analysis.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.main.execution_arn}/*/*"
}

# Session Handlers Lambda Function
resource "aws_lambda_function" "session_handlers" {
  filename         = "session_handlers.zip"
  function_name    = "${local.name_prefix}-session-handlers"
  role            = aws_iam_role.lambda_execution_role.arn
  handler         = "session_handlers.lambda_handler"
  runtime         = var.lambda_runtime
  timeout         = var.lambda_timeout
  memory_size     = var.lambda_memory_size
  
  environment {
    variables = {
      SESSIONS_TABLE_NAME      = aws_dynamodb_table.sessions.name
      USERS_TABLE_NAME         = aws_dynamodb_table.users.name
      REDFLAGS_TABLE_NAME      = aws_dynamodb_table.redflags.name
      API_KEYS_TABLE_NAME      = aws_dynamodb_table.api_keys.name
      RATE_LIMITS_TABLE_NAME   = aws_dynamodb_table.rate_limits.name
      COGNITO_USER_POOL_ID     = aws_cognito_user_pool.main.id
    }
  }
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-session-handlers"
  })
}

# Lambda permission for API Gateway to invoke session handlers
resource "aws_lambda_permission" "session_handlers" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.session_handlers.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.main.execution_arn}/*/*"
}

# Red Flag Handlers Lambda Function
resource "aws_lambda_function" "redflag_handlers" {
  filename         = "redflag_handlers.zip"
  function_name    = "${local.name_prefix}-redflag-handlers"
  role            = aws_iam_role.lambda_execution_role.arn
  handler         = "redflag_handlers.lambda_handler"
  runtime         = var.lambda_runtime
  timeout         = var.lambda_timeout
  memory_size     = var.lambda_memory_size
  
  environment {
    variables = {
      REDFLAGS_TABLE_NAME      = aws_dynamodb_table.redflags.name
      SESSIONS_TABLE_NAME      = aws_dynamodb_table.sessions.name
      NOTIFICATIONS_TABLE_NAME = aws_dynamodb_table.notifications.name
      COGNITO_USER_POOL_ID     = aws_cognito_user_pool.main.id
    }
  }
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-redflag-handlers"
  })
}

# Lambda permission for API Gateway to invoke red flag handlers
resource "aws_lambda_permission" "redflag_handlers" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.redflag_handlers.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.main.execution_arn}/*/*"
}

# API Key Management Lambda Function
resource "aws_lambda_function" "api_key_handlers" {
  filename         = "api_key_handlers.zip"
  function_name    = "${local.name_prefix}-api-key-handlers"
  role            = aws_iam_role.lambda_execution_role.arn
  handler         = "api_key_handlers.lambda_handler"
  runtime         = var.lambda_runtime
  timeout         = var.lambda_timeout
  memory_size     = var.lambda_memory_size
  
  environment {
    variables = {
      API_KEYS_TABLE_NAME  = aws_dynamodb_table.api_keys.name
      USERS_TABLE_NAME     = aws_dynamodb_table.users.name
      COGNITO_USER_POOL_ID = aws_cognito_user_pool.main.id
    }
  }
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-api-key-handlers"
  })
}

# Lambda permission for API Gateway to invoke API key handlers
resource "aws_lambda_permission" "api_key_handlers" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api_key_handlers.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.main.execution_arn}/*/*"
}

# Notification Handlers Lambda Function
resource "aws_lambda_function" "notification_handlers" {
  filename         = "notification_handlers.zip"
  function_name    = "${local.name_prefix}-notification-handlers"
  role            = aws_iam_role.lambda_execution_role.arn
  handler         = "notification_handlers.lambda_handler"
  runtime         = var.lambda_runtime
  timeout         = var.lambda_timeout
  memory_size     = var.lambda_memory_size
  
  environment {
    variables = {
      NOTIFICATIONS_TABLE_NAME = aws_dynamodb_table.notifications.name
      USERS_TABLE_NAME         = aws_dynamodb_table.users.name
      COGNITO_USER_POOL_ID     = aws_cognito_user_pool.main.id
    }
  }
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-notification-handlers"
  })
}

# Lambda permission for API Gateway to invoke notification handlers
resource "aws_lambda_permission" "notification_handlers" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.notification_handlers.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.main.execution_arn}/*/*"
}
