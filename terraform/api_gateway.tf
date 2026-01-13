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
    aws_api_gateway_method.health_check,
    aws_api_gateway_integration.health_check,
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
    aws_api_gateway_integration.auth_enable_mfa
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
  
  type                 = "MOCK"
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
      status  = "healthy"
      service = "ai-therapy-platform"
      timestamp = "$context.requestTime"
    })
  }
}

# Authentication Lambda Function
resource "aws_lambda_function" "auth_handlers" {
  filename         = "auth_handlers.zip"
  function_name    = "${local.name_prefix}-auth-handlers"
  role            = aws_iam_role.lambda_execution_role.arn
  handler         = "auth_handlers.lambda_handler"
  runtime         = var.lambda_runtime
  timeout         = var.lambda_timeout
  memory_size     = var.lambda_memory_size
  
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
  type                   = "AWS_PROXY"
  uri                    = aws_lambda_function.auth_handlers.invoke_arn
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
  type                   = "AWS_PROXY"
  uri                    = aws_lambda_function.auth_handlers.invoke_arn
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
  type                   = "AWS_PROXY"
  uri                    = aws_lambda_function.auth_handlers.invoke_arn
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
  type                   = "AWS_PROXY"
  uri                    = aws_lambda_function.auth_handlers.invoke_arn
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
  type                   = "AWS_PROXY"
  uri                    = aws_lambda_function.auth_handlers.invoke_arn
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
  type                   = "AWS_PROXY"
  uri                    = aws_lambda_function.auth_handlers.invoke_arn
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
  type                   = "AWS_PROXY"
  uri                    = aws_lambda_function.auth_handlers.invoke_arn
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
  type                   = "AWS_PROXY"
  uri                    = aws_lambda_function.auth_handlers.invoke_arn
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
      requestId    = "$context.requestId"
      ip           = "$context.identity.sourceIp"
      requestTime  = "$context.requestTime"
      routeKey     = "$context.routeKey"
      status       = "$context.status"
      protocol     = "$context.protocol"
      responseLength = "$context.responseLength"
      error        = "$context.error.message"
      errorType    = "$context.error.messageString"
      connectionId = "$context.connectionId"
    })
  }
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-websocket-stage"
  })
}

# WebSocket Routes (will be configured with Lambda functions later)
resource "aws_apigatewayv2_route" "connect" {
  api_id    = aws_apigatewayv2_api.websocket.id
  route_key = "$connect"
  
  authorization_type = "AWS_IAM"
}

resource "aws_apigatewayv2_route" "disconnect" {
  api_id    = aws_apigatewayv2_api.websocket.id
  route_key = "$disconnect"
}

resource "aws_apigatewayv2_route" "default" {
  api_id    = aws_apigatewayv2_api.websocket.id
  route_key = "$default"
}

# API Gateway Account (for CloudWatch logging)
resource "aws_api_gateway_account" "main" {
  cloudwatch_role_arn = aws_iam_role.api_gateway_cloudwatch_role.arn
}