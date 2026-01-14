# API Gateway Routes for Frontend Integration
# 🏆 Breaking Barriers UK 2026 compliant

# Lambda function for API handlers
resource "aws_lambda_function" "api_handlers" {
  filename         = "${path.module}/../backend/lambda_packages/api_handlers.zip"
  function_name    = "${var.project_name}-${var.environment}-api-handlers"
  role            = aws_iam_role.lambda_execution_role.arn
  handler         = "lambda_functions.api_handlers.handler"
  runtime         = "python3.9"
  timeout         = 30
  memory_size     = 512
  source_code_hash = fileexists("${path.module}/../backend/lambda_packages/api_handlers.zip") ? filebase64sha256("${path.module}/../backend/lambda_packages/api_handlers.zip") : null

  environment {
    variables = {
      ENVIRONMENT              = var.environment
      USERS_TABLE_NAME         = aws_dynamodb_table.users.name
      SESSIONS_TABLE_NAME      = aws_dynamodb_table.sessions.name
      RED_FLAGS_TABLE_NAME     = aws_dynamodb_table.redflags.name
      NOTIFICATIONS_TABLE_NAME = aws_dynamodb_table.notifications.name
      COGNITO_USER_POOL_ID     = aws_cognito_user_pool.main.id
    }
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-api-handlers"
    Environment = var.environment
    Project     = var.project_name
  }
}

# CloudWatch Log Group for API handlers
resource "aws_cloudwatch_log_group" "api_handlers" {
  name              = "/aws/lambda/${aws_lambda_function.api_handlers.function_name}"
  retention_in_days = 7

  tags = {
    Name        = "${var.project_name}-${var.environment}-api-handlers-logs"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Lambda permission for API Gateway to invoke API handlers
resource "aws_lambda_permission" "api_handlers" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api_handlers.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.main.execution_arn}/*/*"
}

# API Gateway integration for API handlers
resource "aws_apigatewayv2_integration" "api_handlers" {
  api_id           = aws_apigatewayv2_api.main.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.api_handlers.invoke_arn
  integration_method = "POST"
  payload_format_version = "2.0"
}

# ============================================================================
# Authentication Routes
# ============================================================================

resource "aws_apigatewayv2_route" "get_profile" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "GET /auth/profile"
  target    = "integrations/${aws_apigatewayv2_integration.api_handlers.id}"
  authorization_type = "JWT"
  authorizer_id = aws_apigatewayv2_authorizer.cognito.id
}

resource "aws_apigatewayv2_route" "update_profile" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "PUT /auth/profile"
  target    = "integrations/${aws_apigatewayv2_integration.api_handlers.id}"
  authorization_type = "JWT"
  authorizer_id = aws_apigatewayv2_authorizer.cognito.id
}

# ============================================================================
# User Management Routes
# ============================================================================

resource "aws_apigatewayv2_route" "get_user_sessions" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "GET /users/{userId}/sessions"
  target    = "integrations/${aws_apigatewayv2_integration.api_handlers.id}"
  authorization_type = "JWT"
  authorizer_id = aws_apigatewayv2_authorizer.cognito.id
}

# ============================================================================
# Session Management Routes
# ============================================================================

resource "aws_apigatewayv2_route" "create_session" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "POST /sessions"
  target    = "integrations/${aws_apigatewayv2_integration.api_handlers.id}"
  authorization_type = "JWT"
  authorizer_id = aws_apigatewayv2_authorizer.cognito.id
}

resource "aws_apigatewayv2_route" "get_session" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "GET /sessions/{sessionId}"
  target    = "integrations/${aws_apigatewayv2_integration.api_handlers.id}"
  authorization_type = "JWT"
  authorizer_id = aws_apigatewayv2_authorizer.cognito.id
}

resource "aws_apigatewayv2_route" "end_session" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "POST /sessions/{sessionId}/end"
  target    = "integrations/${aws_apigatewayv2_integration.api_handlers.id}"
  authorization_type = "JWT"
  authorizer_id = aws_apigatewayv2_authorizer.cognito.id
}

resource "aws_apigatewayv2_route" "list_sessions" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "GET /sessions"
  target    = "integrations/${aws_apigatewayv2_integration.api_handlers.id}"
  authorization_type = "JWT"
  authorizer_id = aws_apigatewayv2_authorizer.cognito.id
}

# ============================================================================
# Red Flags Routes (Therapist)
# ============================================================================

resource "aws_apigatewayv2_route" "get_therapist_red_flags" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "GET /therapists/{therapistId}/red-flags"
  target    = "integrations/${aws_apigatewayv2_integration.api_handlers.id}"
  authorization_type = "JWT"
  authorizer_id = aws_apigatewayv2_authorizer.cognito.id
}

resource "aws_apigatewayv2_route" "acknowledge_red_flag" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "POST /red-flags/{flagId}/acknowledge"
  target    = "integrations/${aws_apigatewayv2_integration.api_handlers.id}"
  authorization_type = "JWT"
  authorizer_id = aws_apigatewayv2_authorizer.cognito.id
}

resource "aws_apigatewayv2_route" "resolve_red_flag" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "POST /red-flags/{flagId}/resolve"
  target    = "integrations/${aws_apigatewayv2_integration.api_handlers.id}"
  authorization_type = "JWT"
  authorizer_id = aws_apigatewayv2_authorizer.cognito.id
}

# ============================================================================
# Notifications Routes
# ============================================================================

resource "aws_apigatewayv2_route" "get_user_notifications" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "GET /users/{userId}/notifications"
  target    = "integrations/${aws_apigatewayv2_integration.api_handlers.id}"
  authorization_type = "JWT"
  authorizer_id = aws_apigatewayv2_authorizer.cognito.id
}

resource "aws_apigatewayv2_route" "mark_notification_read" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "POST /notifications/{notificationId}/read"
  target    = "integrations/${aws_apigatewayv2_integration.api_handlers.id}"
  authorization_type = "JWT"
  authorizer_id = aws_apigatewayv2_authorizer.cognito.id
}

# ============================================================================
# Admin Routes
# ============================================================================

resource "aws_apigatewayv2_route" "get_admin_stats" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "GET /admin/stats"
  target    = "integrations/${aws_apigatewayv2_integration.api_handlers.id}"
  authorization_type = "JWT"
  authorizer_id = aws_apigatewayv2_authorizer.cognito.id
}

resource "aws_apigatewayv2_route" "get_all_users" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "GET /admin/users"
  target    = "integrations/${aws_apigatewayv2_integration.api_handlers.id}"
  authorization_type = "JWT"
  authorizer_id = aws_apigatewayv2_authorizer.cognito.id
}

resource "aws_apigatewayv2_route" "get_all_sessions" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "GET /admin/sessions"
  target    = "integrations/${aws_apigatewayv2_integration.api_handlers.id}"
  authorization_type = "JWT"
  authorizer_id = aws_apigatewayv2_authorizer.cognito.id
}

resource "aws_apigatewayv2_route" "get_all_red_flags" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "GET /admin/red-flags"
  target    = "integrations/${aws_apigatewayv2_integration.api_handlers.id}"
  authorization_type = "JWT"
  authorizer_id = aws_apigatewayv2_authorizer.cognito.id
}

# ============================================================================
# CORS Configuration
# ============================================================================

resource "aws_apigatewayv2_route" "options_auth" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "OPTIONS /auth/{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.api_handlers.id}"
}

resource "aws_apigatewayv2_route" "options_users" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "OPTIONS /users/{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.api_handlers.id}"
}

resource "aws_apigatewayv2_route" "options_sessions" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "OPTIONS /sessions/{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.api_handlers.id}"
}

resource "aws_apigatewayv2_route" "options_therapists" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "OPTIONS /therapists/{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.api_handlers.id}"
}

resource "aws_apigatewayv2_route" "options_red_flags" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "OPTIONS /red-flags/{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.api_handlers.id}"
}

resource "aws_apigatewayv2_route" "options_notifications" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "OPTIONS /notifications/{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.api_handlers.id}"
}

resource "aws_apigatewayv2_route" "options_admin" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "OPTIONS /admin/{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.api_handlers.id}"
}

# ============================================================================
# Outputs
# ============================================================================

output "api_handlers_function_name" {
  description = "Name of the API handlers Lambda function"
  value       = aws_lambda_function.api_handlers.function_name
}

output "api_handlers_function_arn" {
  description = "ARN of the API handlers Lambda function"
  value       = aws_lambda_function.api_handlers.arn
}
