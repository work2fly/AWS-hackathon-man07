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
    aws_api_gateway_integration.health_check
  ]
  
  rest_api_id = aws_api_gateway_rest_api.main.id
  stage_name  = var.api_gateway_stage_name
  
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
  
  # Throttling settings
  throttle_settings {
    rate_limit  = var.api_throttle_rate_limit
    burst_limit = var.api_throttle_burst_limit
  }
  
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
  
  # Throttling
  throttle_settings {
    rate_limit  = var.api_throttle_rate_limit
    burst_limit = var.api_throttle_burst_limit
  }
  
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