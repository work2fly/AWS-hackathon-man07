# AI Therapy Platform - API Gateway Resources
# Breaking Barriers UK 2026 compliant API configuration

# REST API Gateway
resource "aws_api_gateway_rest_api" "main" {
  name        = "${local.name_prefix}-rest-api"
  description = "AI Therapy Platform REST API"

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  # Binary media types for audio handling
  binary_media_types = [
    "audio/*",
    "application/octet-stream"
  ]

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-rest-api"
  })
}

# API Gateway Deployment
resource "aws_api_gateway_deployment" "main" {
  depends_on = [
    # Health check
    aws_api_gateway_method.health_check,
    aws_api_gateway_integration.health_check,
    # Auth endpoints
    aws_api_gateway_method.auth_register,
    aws_api_gateway_integration.auth_register,
    aws_api_gateway_method.auth_login,
    aws_api_gateway_integration.auth_login,
    aws_api_gateway_method.auth_logout,
    aws_api_gateway_integration.auth_logout,
    aws_api_gateway_method.auth_refresh,
    aws_api_gateway_integration.auth_refresh,
    aws_api_gateway_method.auth_reset_password,
    aws_api_gateway_integration.auth_reset_password,
    aws_api_gateway_method.auth_profile_get,
    aws_api_gateway_integration.auth_profile_get,
    aws_api_gateway_method.auth_profile_put,
    aws_api_gateway_integration.auth_profile_put,
    aws_api_gateway_method.auth_enable_mfa,
    aws_api_gateway_integration.auth_enable_mfa,
    # User endpoints
    aws_api_gateway_method.users_get,
    aws_api_gateway_integration.users_get,
    aws_api_gateway_method.users_put,
    aws_api_gateway_integration.users_put,
    aws_api_gateway_method.users_sessions_get,
    aws_api_gateway_integration.users_sessions_get,
    aws_api_gateway_method.users_notifications_get,
    aws_api_gateway_integration.users_notifications_get,
    # Session endpoints
    aws_api_gateway_method.sessions_post,
    aws_api_gateway_integration.sessions_post,
    aws_api_gateway_method.sessions_get,
    aws_api_gateway_integration.sessions_get,
    aws_api_gateway_method.sessions_session_id_get,
    aws_api_gateway_integration.sessions_session_id_get,
    aws_api_gateway_method.sessions_end_post,
    aws_api_gateway_integration.sessions_end_post,
    # Therapist red flags endpoints
    aws_api_gateway_method.therapists_red_flags_get,
    aws_api_gateway_integration.therapists_red_flags_get,
    # Red flags endpoints
    aws_api_gateway_method.red_flags_acknowledge_post,
    aws_api_gateway_integration.red_flags_acknowledge_post,
    aws_api_gateway_method.red_flags_resolve_post,
    aws_api_gateway_integration.red_flags_resolve_post,
    # Notification endpoints
    aws_api_gateway_method.notifications_read_post,
    aws_api_gateway_integration.notifications_read_post,
    # Admin endpoints
    aws_api_gateway_method.admin_stats_get,
    aws_api_gateway_integration.admin_stats_get,
    aws_api_gateway_method.admin_users_get,
    aws_api_gateway_integration.admin_users_get,
    aws_api_gateway_method.admin_sessions_get,
    aws_api_gateway_integration.admin_sessions_get,
    aws_api_gateway_method.admin_red_flags_get,
    aws_api_gateway_integration.admin_red_flags_get
  ]

  rest_api_id = aws_api_gateway_rest_api.main.id

  lifecycle {
    create_before_destroy = true
  }
}

# API Gateway Stage
resource "aws_api_gateway_stage" "main" {
  deployment_id = aws_api_gateway_deployment.main.id
  rest_api_id   = aws_api_gateway_rest_api.main.id
  stage_name    = var.api_gateway_stage_name

  # Enable detailed CloudWatch metrics
  xray_tracing_enabled = var.enable_detailed_monitoring

  # Access logging
  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gateway.arn
    format = jsonencode({
      requestId      = "$context.requestId"
      ip             = "$context.identity.sourceIp"
      caller         = "$context.identity.caller"
      user           = "$context.identity.user"
      requestTime    = "$context.requestTime"
      httpMethod     = "$context.httpMethod"
      resourcePath   = "$context.resourcePath"
      status         = "$context.status"
      protocol       = "$context.protocol"
      responseLength = "$context.responseLength"
      error          = "$context.error.message"
      errorType      = "$context.error.messageString"
    })
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-api-stage"
  })
}

# Health check resource
resource "aws_api_gateway_resource" "health" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_rest_api.main.root_resource_id
  path_part   = "health"
}

# Health check method
resource "aws_api_gateway_method" "health_check" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.health.id
  http_method   = "GET"
  authorization = "NONE"
}

# Health check integration
resource "aws_api_gateway_integration" "health_check" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.health.id
  http_method = aws_api_gateway_method.health_check.http_method

  type                    = "MOCK"
  integration_http_method = "POST"

  request_templates = {
    "application/json" = jsonencode({
      statusCode = 200
    })
  }
}

# Health check method response
resource "aws_api_gateway_method_response" "health_check" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.health.id
  http_method = aws_api_gateway_method.health_check.http_method
  status_code = "200"

  response_models = {
    "application/json" = "Empty"
  }
}

# Health check integration response
resource "aws_api_gateway_integration_response" "health_check" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.health.id
  http_method = aws_api_gateway_method.health_check.http_method
  status_code = aws_api_gateway_method_response.health_check.status_code

  response_templates = {
    "application/json" = jsonencode({
      status    = "healthy"
      service   = "ai-therapy-platform"
      timestamp = "$context.requestTime"
    })
  }

  depends_on = [aws_api_gateway_integration.health_check]
}

# Authentication Lambda Function
resource "aws_lambda_function" "auth_handlers" {
  filename      = "auth_handlers.zip"
  function_name = "${local.name_prefix}-auth-handlers"
  role          = aws_iam_role.lambda_execution_role.arn
  handler       = "auth_handlers.lambda_handler"
  runtime       = var.lambda_runtime
  timeout       = var.lambda_timeout
  memory_size   = var.lambda_memory_size

  environment {
    variables = {
      COGNITO_USER_POOL_ID = aws_cognito_user_pool.main.id
      COGNITO_CLIENT_ID    = aws_cognito_user_pool_client.main.id
      USERS_TABLE_NAME     = aws_dynamodb_table.users.name
    }
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-auth-handlers"
  })
}

# Lambda permission for API Gateway to invoke auth function
resource "aws_lambda_permission" "auth_handlers" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.auth_handlers.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.main.execution_arn}/*/*"
}

# Auth resource
resource "aws_api_gateway_resource" "auth" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_rest_api.main.root_resource_id
  path_part   = "auth"
}

# Auth register resource
resource "aws_api_gateway_resource" "auth_register" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.auth.id
  path_part   = "register"
}

# Auth register method
resource "aws_api_gateway_method" "auth_register" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.auth_register.id
  http_method   = "POST"
  authorization = "NONE"
}

# Auth register integration
resource "aws_api_gateway_integration" "auth_register" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.auth_register.id
  http_method = aws_api_gateway_method.auth_register.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.auth_handlers.invoke_arn
}

# Auth login resource
resource "aws_api_gateway_resource" "auth_login" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.auth.id
  path_part   = "login"
}

# Auth login method
resource "aws_api_gateway_method" "auth_login" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.auth_login.id
  http_method   = "POST"
  authorization = "NONE"
}

# Auth login integration
resource "aws_api_gateway_integration" "auth_login" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.auth_login.id
  http_method = aws_api_gateway_method.auth_login.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.auth_handlers.invoke_arn
}

# Auth logout resource
resource "aws_api_gateway_resource" "auth_logout" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.auth.id
  path_part   = "logout"
}

# Auth logout method
resource "aws_api_gateway_method" "auth_logout" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.auth_logout.id
  http_method   = "POST"
  authorization = "NONE"
}

# Auth logout integration
resource "aws_api_gateway_integration" "auth_logout" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.auth_logout.id
  http_method = aws_api_gateway_method.auth_logout.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.auth_handlers.invoke_arn
}

# Auth refresh resource
resource "aws_api_gateway_resource" "auth_refresh" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.auth.id
  path_part   = "refresh"
}

# Auth refresh method
resource "aws_api_gateway_method" "auth_refresh" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.auth_refresh.id
  http_method   = "POST"
  authorization = "NONE"
}

# Auth refresh integration
resource "aws_api_gateway_integration" "auth_refresh" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.auth_refresh.id
  http_method = aws_api_gateway_method.auth_refresh.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.auth_handlers.invoke_arn
}

# Auth reset-password resource
resource "aws_api_gateway_resource" "auth_reset_password" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.auth.id
  path_part   = "reset-password"
}

# Auth reset-password method
resource "aws_api_gateway_method" "auth_reset_password" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.auth_reset_password.id
  http_method   = "POST"
  authorization = "NONE"
}

# Auth reset-password integration
resource "aws_api_gateway_integration" "auth_reset_password" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.auth_reset_password.id
  http_method = aws_api_gateway_method.auth_reset_password.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.auth_handlers.invoke_arn
}

# Auth profile resource
resource "aws_api_gateway_resource" "auth_profile" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.auth.id
  path_part   = "profile"
}

# Auth profile GET method
resource "aws_api_gateway_method" "auth_profile_get" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.auth_profile.id
  http_method   = "GET"
  authorization = "NONE"
}

# Auth profile GET integration
resource "aws_api_gateway_integration" "auth_profile_get" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.auth_profile.id
  http_method = aws_api_gateway_method.auth_profile_get.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.auth_handlers.invoke_arn
}

# Auth profile PUT method
resource "aws_api_gateway_method" "auth_profile_put" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.auth_profile.id
  http_method   = "PUT"
  authorization = "NONE"
}

# Auth profile PUT integration
resource "aws_api_gateway_integration" "auth_profile_put" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.auth_profile.id
  http_method = aws_api_gateway_method.auth_profile_put.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.auth_handlers.invoke_arn
}

# Auth enable-mfa resource
resource "aws_api_gateway_resource" "auth_enable_mfa" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.auth.id
  path_part   = "enable-mfa"
}

# Auth enable-mfa method
resource "aws_api_gateway_method" "auth_enable_mfa" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.auth_enable_mfa.id
  http_method   = "POST"
  authorization = "NONE"
}

# Auth enable-mfa integration
resource "aws_api_gateway_integration" "auth_enable_mfa" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.auth_enable_mfa.id
  http_method = aws_api_gateway_method.auth_enable_mfa.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.auth_handlers.invoke_arn
}

# WebSocket API Gateway
resource "aws_apigatewayv2_api" "websocket" {
  name                       = "${local.name_prefix}-websocket-api"
  description                = "AI Therapy Platform WebSocket API for real-time communication"
  protocol_type              = "WEBSOCKET"
  route_selection_expression = "$request.body.action"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-websocket-api"
  })
}

# WebSocket API Stage
resource "aws_apigatewayv2_stage" "websocket" {
  api_id      = aws_apigatewayv2_api.websocket.id
  name        = var.api_gateway_stage_name
  auto_deploy = true

  # Access logging
  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gateway_websocket.arn
    format = jsonencode({
      requestId      = "$context.requestId"
      ip             = "$context.identity.sourceIp"
      requestTime    = "$context.requestTime"
      routeKey       = "$context.routeKey"
      status         = "$context.status"
      protocol       = "$context.protocol"
      responseLength = "$context.responseLength"
      error          = "$context.error.message"
      errorType      = "$context.error.messageString"
      connectionId   = "$context.connectionId"
    })
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-websocket-stage"
  })
}

# WebSocket Connection Handler Lambda Function
resource "aws_lambda_function" "websocket_connect" {
  filename      = "websocket_handlers.zip"
  function_name = "${local.name_prefix}-websocket-connect"
  role          = aws_iam_role.lambda_execution_role.arn
  handler       = "websocket_handlers.connect_handler"
  runtime       = var.lambda_runtime
  timeout       = var.lambda_timeout
  memory_size   = var.lambda_memory_size

  environment {
    variables = {
      CONNECTIONS_TABLE_NAME = aws_dynamodb_table.websocket_connections.name
      SESSIONS_TABLE_NAME    = aws_dynamodb_table.sessions.name
      COGNITO_USER_POOL_ID   = aws_cognito_user_pool.main.id
      WEBSOCKET_API_ENDPOINT = aws_apigatewayv2_stage.websocket.invoke_url
    }
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-websocket-connect"
  })
}

# WebSocket Disconnect Handler Lambda Function
resource "aws_lambda_function" "websocket_disconnect" {
  filename      = "websocket_handlers.zip"
  function_name = "${local.name_prefix}-websocket-disconnect"
  role          = aws_iam_role.lambda_execution_role.arn
  handler       = "websocket_handlers.disconnect_handler"
  runtime       = var.lambda_runtime
  timeout       = var.lambda_timeout
  memory_size   = var.lambda_memory_size

  environment {
    variables = {
      CONNECTIONS_TABLE_NAME = aws_dynamodb_table.websocket_connections.name
      SESSIONS_TABLE_NAME    = aws_dynamodb_table.sessions.name
      WEBSOCKET_API_ENDPOINT = aws_apigatewayv2_stage.websocket.invoke_url
    }
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-websocket-disconnect"
  })
}

# WebSocket Default Handler Lambda Function
resource "aws_lambda_function" "websocket_default" {
  filename      = "websocket_handlers.zip"
  function_name = "${local.name_prefix}-websocket-default"
  role          = aws_iam_role.lambda_execution_role.arn
  handler       = "websocket_handlers.default_handler"
  runtime       = var.lambda_runtime
  timeout       = var.lambda_timeout
  memory_size   = var.lambda_memory_size

  environment {
    variables = {
      CONNECTIONS_TABLE_NAME = aws_dynamodb_table.websocket_connections.name
      SESSIONS_TABLE_NAME    = aws_dynamodb_table.sessions.name
      WEBSOCKET_API_ENDPOINT = aws_apigatewayv2_stage.websocket.invoke_url
      BEDROCK_MODEL_ID       = var.bedrock_model_id
    }
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-websocket-default"
  })
}

# Lambda permissions for WebSocket API Gateway
resource "aws_lambda_permission" "websocket_connect" {
  statement_id  = "AllowWebSocketAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.websocket_connect.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.websocket.execution_arn}/*/*"
}

resource "aws_lambda_permission" "websocket_disconnect" {
  statement_id  = "AllowWebSocketAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.websocket_disconnect.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.websocket.execution_arn}/*/*"
}

resource "aws_lambda_permission" "websocket_default" {
  statement_id  = "AllowWebSocketAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.websocket_default.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.websocket.execution_arn}/*/*"
}

# WebSocket Route Integrations
resource "aws_apigatewayv2_integration" "connect" {
  api_id           = aws_apigatewayv2_api.websocket.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.websocket_connect.invoke_arn
}

resource "aws_apigatewayv2_integration" "disconnect" {
  api_id           = aws_apigatewayv2_api.websocket.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.websocket_disconnect.invoke_arn
}

resource "aws_apigatewayv2_integration" "default" {
  api_id           = aws_apigatewayv2_api.websocket.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.websocket_default.invoke_arn
}

# WebSocket Routes with Lambda integrations
resource "aws_apigatewayv2_route" "connect" {
  api_id    = aws_apigatewayv2_api.websocket.id
  route_key = "$connect"
  target    = "integrations/${aws_apigatewayv2_integration.connect.id}"

  authorization_type = "AWS_IAM"
}

resource "aws_apigatewayv2_route" "disconnect" {
  api_id    = aws_apigatewayv2_api.websocket.id
  route_key = "$disconnect"
  target    = "integrations/${aws_apigatewayv2_integration.disconnect.id}"
}

resource "aws_apigatewayv2_route" "default" {
  api_id    = aws_apigatewayv2_api.websocket.id
  route_key = "$default"
  target    = "integrations/${aws_apigatewayv2_integration.default.id}"
}

# API Gateway Account (for CloudWatch logging)
resource "aws_api_gateway_account" "main" {
  cloudwatch_role_arn = aws_iam_role.api_gateway_cloudwatch_role.arn
}


# =============================================================================
# NEW LAMBDA FUNCTIONS AND API GATEWAY ROUTES
# Added for frontend-backend integration (Task 11)
# 🏆 Breaking Barriers UK 2026 compliant
# =============================================================================

# -----------------------------------------------------------------------------
# USER HANDLERS LAMBDA
# Handles: GET /users/{userId}, PUT /users/{userId}, GET /users/{userId}/sessions
# -----------------------------------------------------------------------------

resource "aws_lambda_function" "user_handlers" {
  filename      = "protected_endpoints.zip"
  function_name = "${local.name_prefix}-user-handlers"
  role          = aws_iam_role.lambda_execution_role.arn
  handler       = "user_handlers.lambda_handler"
  runtime       = var.lambda_runtime
  timeout       = var.lambda_timeout
  memory_size   = var.lambda_memory_size

  environment {
    variables = {
      USERS_TABLE_NAME     = aws_dynamodb_table.users.name
      SESSIONS_TABLE_NAME  = aws_dynamodb_table.sessions.name
      COGNITO_USER_POOL_ID = aws_cognito_user_pool.main.id
    }
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-user-handlers"
  })
}

resource "aws_lambda_permission" "user_handlers" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.user_handlers.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.main.execution_arn}/*/*"
}

# -----------------------------------------------------------------------------
# SESSION HANDLERS LAMBDA
# Handles: POST /sessions, GET /sessions/{sessionId}, POST /sessions/{sessionId}/end, GET /sessions
# -----------------------------------------------------------------------------

resource "aws_lambda_function" "session_handlers" {
  filename      = "session_handlers.zip"
  function_name = "${local.name_prefix}-session-handlers"
  role          = aws_iam_role.lambda_execution_role.arn
  handler       = "session_handlers.lambda_handler"
  runtime       = var.lambda_runtime
  timeout       = var.lambda_timeout
  memory_size   = var.lambda_memory_size

  environment {
    variables = {
      SESSIONS_TABLE_NAME  = aws_dynamodb_table.sessions.name
      USERS_TABLE_NAME     = aws_dynamodb_table.users.name
      COGNITO_USER_POOL_ID = aws_cognito_user_pool.main.id
      BEDROCK_MODEL_ID     = var.bedrock_model_id
    }
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-session-handlers"
  })
}

resource "aws_lambda_permission" "session_handlers" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.session_handlers.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.main.execution_arn}/*/*"
}

# -----------------------------------------------------------------------------
# RED FLAG HANDLERS LAMBDA
# Handles: GET /therapists/{therapistId}/red-flags, POST /red-flags/{flagId}/acknowledge, POST /red-flags/{flagId}/resolve
# -----------------------------------------------------------------------------

resource "aws_lambda_function" "red_flag_handlers" {
  filename      = "protected_endpoints.zip"
  function_name = "${local.name_prefix}-red-flag-handlers"
  role          = aws_iam_role.lambda_execution_role.arn
  handler       = "red_flag_handlers.lambda_handler"
  runtime       = var.lambda_runtime
  timeout       = var.lambda_timeout
  memory_size   = var.lambda_memory_size

  environment {
    variables = {
      REDFLAGS_TABLE_NAME  = aws_dynamodb_table.redflags.name
      SESSIONS_TABLE_NAME  = aws_dynamodb_table.sessions.name
      COGNITO_USER_POOL_ID = aws_cognito_user_pool.main.id
    }
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-red-flag-handlers"
  })
}

resource "aws_lambda_permission" "red_flag_handlers" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.red_flag_handlers.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.main.execution_arn}/*/*"
}

# -----------------------------------------------------------------------------
# NOTIFICATION HANDLERS LAMBDA
# Handles: GET /users/{userId}/notifications, POST /notifications/{notificationId}/read
# -----------------------------------------------------------------------------

resource "aws_lambda_function" "notification_handlers" {
  filename      = "protected_endpoints.zip"
  function_name = "${local.name_prefix}-notification-handlers"
  role          = aws_iam_role.lambda_execution_role.arn
  handler       = "notification_handlers.lambda_handler"
  runtime       = var.lambda_runtime
  timeout       = var.lambda_timeout
  memory_size   = var.lambda_memory_size

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

resource "aws_lambda_permission" "notification_handlers" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.notification_handlers.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.main.execution_arn}/*/*"
}

# -----------------------------------------------------------------------------
# ADMIN HANDLERS LAMBDA
# Handles: GET /admin/stats, GET /admin/users, GET /admin/sessions, GET /admin/red-flags
# -----------------------------------------------------------------------------

resource "aws_lambda_function" "admin_handlers" {
  filename      = "protected_endpoints.zip"
  function_name = "${local.name_prefix}-admin-handlers"
  role          = aws_iam_role.lambda_execution_role.arn
  handler       = "admin_handlers.lambda_handler"
  runtime       = var.lambda_runtime
  timeout       = var.lambda_timeout
  memory_size   = var.lambda_memory_size

  environment {
    variables = {
      USERS_TABLE_NAME         = aws_dynamodb_table.users.name
      SESSIONS_TABLE_NAME      = aws_dynamodb_table.sessions.name
      REDFLAGS_TABLE_NAME      = aws_dynamodb_table.redflags.name
      NOTIFICATIONS_TABLE_NAME = aws_dynamodb_table.notifications.name
      COGNITO_USER_POOL_ID     = aws_cognito_user_pool.main.id
    }
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-admin-handlers"
  })
}

resource "aws_lambda_permission" "admin_handlers" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.admin_handlers.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.main.execution_arn}/*/*"
}

# =============================================================================
# API GATEWAY RESOURCES AND ROUTES
# =============================================================================

# -----------------------------------------------------------------------------
# USERS ENDPOINTS
# -----------------------------------------------------------------------------

# /users resource
resource "aws_api_gateway_resource" "users" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_rest_api.main.root_resource_id
  path_part   = "users"
}

# /users/{userId} resource
resource "aws_api_gateway_resource" "users_user_id" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.users.id
  path_part   = "{userId}"
}

# GET /users/{userId}
resource "aws_api_gateway_method" "users_get" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.users_user_id.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "users_get" {
  rest_api_id             = aws_api_gateway_rest_api.main.id
  resource_id             = aws_api_gateway_resource.users_user_id.id
  http_method             = aws_api_gateway_method.users_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.user_handlers.invoke_arn
}

# PUT /users/{userId}
resource "aws_api_gateway_method" "users_put" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.users_user_id.id
  http_method   = "PUT"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "users_put" {
  rest_api_id             = aws_api_gateway_rest_api.main.id
  resource_id             = aws_api_gateway_resource.users_user_id.id
  http_method             = aws_api_gateway_method.users_put.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.user_handlers.invoke_arn
}

# /users/{userId}/sessions resource
resource "aws_api_gateway_resource" "users_sessions" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.users_user_id.id
  path_part   = "sessions"
}

# GET /users/{userId}/sessions
resource "aws_api_gateway_method" "users_sessions_get" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.users_sessions.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "users_sessions_get" {
  rest_api_id             = aws_api_gateway_rest_api.main.id
  resource_id             = aws_api_gateway_resource.users_sessions.id
  http_method             = aws_api_gateway_method.users_sessions_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.user_handlers.invoke_arn
}

# /users/{userId}/notifications resource
resource "aws_api_gateway_resource" "users_notifications" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.users_user_id.id
  path_part   = "notifications"
}

# GET /users/{userId}/notifications
resource "aws_api_gateway_method" "users_notifications_get" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.users_notifications.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "users_notifications_get" {
  rest_api_id             = aws_api_gateway_rest_api.main.id
  resource_id             = aws_api_gateway_resource.users_notifications.id
  http_method             = aws_api_gateway_method.users_notifications_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.notification_handlers.invoke_arn
}

# -----------------------------------------------------------------------------
# SESSIONS ENDPOINTS
# -----------------------------------------------------------------------------

# /sessions resource
resource "aws_api_gateway_resource" "sessions" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_rest_api.main.root_resource_id
  path_part   = "sessions"
}

# POST /sessions
resource "aws_api_gateway_method" "sessions_post" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.sessions.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "sessions_post" {
  rest_api_id             = aws_api_gateway_rest_api.main.id
  resource_id             = aws_api_gateway_resource.sessions.id
  http_method             = aws_api_gateway_method.sessions_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.session_handlers.invoke_arn
}

# GET /sessions (admin list all sessions)
resource "aws_api_gateway_method" "sessions_get" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.sessions.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "sessions_get" {
  rest_api_id             = aws_api_gateway_rest_api.main.id
  resource_id             = aws_api_gateway_resource.sessions.id
  http_method             = aws_api_gateway_method.sessions_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.session_handlers.invoke_arn
}

# /sessions/{sessionId} resource
resource "aws_api_gateway_resource" "sessions_session_id" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.sessions.id
  path_part   = "{sessionId}"
}

# GET /sessions/{sessionId}
resource "aws_api_gateway_method" "sessions_session_id_get" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.sessions_session_id.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "sessions_session_id_get" {
  rest_api_id             = aws_api_gateway_rest_api.main.id
  resource_id             = aws_api_gateway_resource.sessions_session_id.id
  http_method             = aws_api_gateway_method.sessions_session_id_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.session_handlers.invoke_arn
}

# /sessions/{sessionId}/end resource
resource "aws_api_gateway_resource" "sessions_end" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.sessions_session_id.id
  path_part   = "end"
}

# POST /sessions/{sessionId}/end
resource "aws_api_gateway_method" "sessions_end_post" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.sessions_end.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "sessions_end_post" {
  rest_api_id             = aws_api_gateway_rest_api.main.id
  resource_id             = aws_api_gateway_resource.sessions_end.id
  http_method             = aws_api_gateway_method.sessions_end_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.session_handlers.invoke_arn
}

# -----------------------------------------------------------------------------
# THERAPISTS ENDPOINTS (Red Flags)
# -----------------------------------------------------------------------------

# /therapists resource
resource "aws_api_gateway_resource" "therapists" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_rest_api.main.root_resource_id
  path_part   = "therapists"
}

# /therapists/{therapistId} resource
resource "aws_api_gateway_resource" "therapists_therapist_id" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.therapists.id
  path_part   = "{therapistId}"
}

# /therapists/{therapistId}/red-flags resource
resource "aws_api_gateway_resource" "therapists_red_flags" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.therapists_therapist_id.id
  path_part   = "red-flags"
}

# GET /therapists/{therapistId}/red-flags
resource "aws_api_gateway_method" "therapists_red_flags_get" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.therapists_red_flags.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "therapists_red_flags_get" {
  rest_api_id             = aws_api_gateway_rest_api.main.id
  resource_id             = aws_api_gateway_resource.therapists_red_flags.id
  http_method             = aws_api_gateway_method.therapists_red_flags_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.red_flag_handlers.invoke_arn
}

# -----------------------------------------------------------------------------
# RED FLAGS ENDPOINTS
# -----------------------------------------------------------------------------

# /red-flags resource
resource "aws_api_gateway_resource" "red_flags" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_rest_api.main.root_resource_id
  path_part   = "red-flags"
}

# /red-flags/{flagId} resource
resource "aws_api_gateway_resource" "red_flags_flag_id" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.red_flags.id
  path_part   = "{flagId}"
}

# /red-flags/{flagId}/acknowledge resource
resource "aws_api_gateway_resource" "red_flags_acknowledge" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.red_flags_flag_id.id
  path_part   = "acknowledge"
}

# POST /red-flags/{flagId}/acknowledge
resource "aws_api_gateway_method" "red_flags_acknowledge_post" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.red_flags_acknowledge.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "red_flags_acknowledge_post" {
  rest_api_id             = aws_api_gateway_rest_api.main.id
  resource_id             = aws_api_gateway_resource.red_flags_acknowledge.id
  http_method             = aws_api_gateway_method.red_flags_acknowledge_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.red_flag_handlers.invoke_arn
}

# /red-flags/{flagId}/resolve resource
resource "aws_api_gateway_resource" "red_flags_resolve" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.red_flags_flag_id.id
  path_part   = "resolve"
}

# POST /red-flags/{flagId}/resolve
resource "aws_api_gateway_method" "red_flags_resolve_post" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.red_flags_resolve.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "red_flags_resolve_post" {
  rest_api_id             = aws_api_gateway_rest_api.main.id
  resource_id             = aws_api_gateway_resource.red_flags_resolve.id
  http_method             = aws_api_gateway_method.red_flags_resolve_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.red_flag_handlers.invoke_arn
}

# -----------------------------------------------------------------------------
# NOTIFICATIONS ENDPOINTS
# -----------------------------------------------------------------------------

# /notifications resource
resource "aws_api_gateway_resource" "notifications" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_rest_api.main.root_resource_id
  path_part   = "notifications"
}

# /notifications/{notificationId} resource
resource "aws_api_gateway_resource" "notifications_notification_id" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.notifications.id
  path_part   = "{notificationId}"
}

# /notifications/{notificationId}/read resource
resource "aws_api_gateway_resource" "notifications_read" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.notifications_notification_id.id
  path_part   = "read"
}

# POST /notifications/{notificationId}/read
resource "aws_api_gateway_method" "notifications_read_post" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.notifications_read.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "notifications_read_post" {
  rest_api_id             = aws_api_gateway_rest_api.main.id
  resource_id             = aws_api_gateway_resource.notifications_read.id
  http_method             = aws_api_gateway_method.notifications_read_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.notification_handlers.invoke_arn
}

# -----------------------------------------------------------------------------
# ADMIN ENDPOINTS
# -----------------------------------------------------------------------------

# /admin resource
resource "aws_api_gateway_resource" "admin" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_rest_api.main.root_resource_id
  path_part   = "admin"
}

# /admin/stats resource
resource "aws_api_gateway_resource" "admin_stats" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.admin.id
  path_part   = "stats"
}

# GET /admin/stats
resource "aws_api_gateway_method" "admin_stats_get" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.admin_stats.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "admin_stats_get" {
  rest_api_id             = aws_api_gateway_rest_api.main.id
  resource_id             = aws_api_gateway_resource.admin_stats.id
  http_method             = aws_api_gateway_method.admin_stats_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.admin_handlers.invoke_arn
}

# /admin/users resource
resource "aws_api_gateway_resource" "admin_users" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.admin.id
  path_part   = "users"
}

# GET /admin/users
resource "aws_api_gateway_method" "admin_users_get" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.admin_users.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "admin_users_get" {
  rest_api_id             = aws_api_gateway_rest_api.main.id
  resource_id             = aws_api_gateway_resource.admin_users.id
  http_method             = aws_api_gateway_method.admin_users_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.admin_handlers.invoke_arn
}

# /admin/sessions resource
resource "aws_api_gateway_resource" "admin_sessions" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.admin.id
  path_part   = "sessions"
}

# GET /admin/sessions
resource "aws_api_gateway_method" "admin_sessions_get" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.admin_sessions.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "admin_sessions_get" {
  rest_api_id             = aws_api_gateway_rest_api.main.id
  resource_id             = aws_api_gateway_resource.admin_sessions.id
  http_method             = aws_api_gateway_method.admin_sessions_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.admin_handlers.invoke_arn
}

# /admin/red-flags resource
resource "aws_api_gateway_resource" "admin_red_flags" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.admin.id
  path_part   = "red-flags"
}

# GET /admin/red-flags
resource "aws_api_gateway_method" "admin_red_flags_get" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.admin_red_flags.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "admin_red_flags_get" {
  rest_api_id             = aws_api_gateway_rest_api.main.id
  resource_id             = aws_api_gateway_resource.admin_red_flags.id
  http_method             = aws_api_gateway_method.admin_red_flags_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.admin_handlers.invoke_arn
}
