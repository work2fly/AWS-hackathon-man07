# AI Therapy Platform - CloudWatch Resources
# Breaking Barriers UK 2026 compliant monitoring and logging

# CloudWatch Log Group for API Gateway
resource "aws_cloudwatch_log_group" "api_gateway" {
  name              = "/aws/apigateway/${local.name_prefix}-rest-api"
  retention_in_days = var.log_retention_days
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-api-gateway-logs"
  })
}

# CloudWatch Log Group for WebSocket API Gateway
resource "aws_cloudwatch_log_group" "api_gateway_websocket" {
  name              = "/aws/apigateway/${local.name_prefix}-websocket-api"
  retention_in_days = var.log_retention_days
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-websocket-logs"
  })
}

# CloudWatch Log Group for Lambda functions
resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${local.name_prefix}"
  retention_in_days = var.log_retention_days
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-lambda-logs"
  })
}

# CloudWatch Dashboard
resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${local.name_prefix}-dashboard"
  
  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6
        
        properties = {
          metrics = [
            ["AWS/ApiGateway", "Count", "ApiName", "${local.name_prefix}-rest-api"],
            [".", "Latency", ".", "."],
            [".", "4XXError", ".", "."],
            [".", "5XXError", ".", "."]
          ]
          view    = "timeSeries"
          stacked = false
          region  = local.region
          title   = "API Gateway Metrics"
          period  = 300
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6
        
        properties = {
          metrics = [
            ["AWS/DynamoDB", "ConsumedReadCapacityUnits", "TableName", aws_dynamodb_table.users.name],
            [".", "ConsumedWriteCapacityUnits", ".", "."],
            [".", "ConsumedReadCapacityUnits", "TableName", aws_dynamodb_table.sessions.name],
            [".", "ConsumedWriteCapacityUnits", ".", "."]
          ]
          view    = "timeSeries"
          stacked = false
          region  = local.region
          title   = "DynamoDB Metrics"
          period  = 300
        }
      },
      {
        type   = "log"
        x      = 0
        y      = 12
        width  = 24
        height = 6
        
        properties = {
          query   = "SOURCE '/aws/lambda/${local.name_prefix}' | fields @timestamp, @message | sort @timestamp desc | limit 100"
          region  = local.region
          title   = "Recent Lambda Logs"
        }
      }
    ]
  })
}

# CloudWatch Alarms

# API Gateway 4XX Error Rate Alarm
resource "aws_cloudwatch_metric_alarm" "api_gateway_4xx_errors" {
  alarm_name          = "${local.name_prefix}-api-gateway-4xx-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "4XXError"
  namespace           = "AWS/ApiGateway"
  period              = "300"
  statistic           = "Sum"
  threshold           = "10"
  alarm_description   = "This metric monitors API Gateway 4XX errors"
  alarm_actions       = []
  
  dimensions = {
    ApiName = "${local.name_prefix}-rest-api"
  }
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-4xx-errors-alarm"
  })
}

# API Gateway 5XX Error Rate Alarm
resource "aws_cloudwatch_metric_alarm" "api_gateway_5xx_errors" {
  alarm_name          = "${local.name_prefix}-api-gateway-5xx-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "5XXError"
  namespace           = "AWS/ApiGateway"
  period              = "300"
  statistic           = "Sum"
  threshold           = "5"
  alarm_description   = "This metric monitors API Gateway 5XX errors"
  alarm_actions       = []
  
  dimensions = {
    ApiName = "${local.name_prefix}-rest-api"
  }
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-5xx-errors-alarm"
  })
}

# API Gateway High Latency Alarm
resource "aws_cloudwatch_metric_alarm" "api_gateway_latency" {
  alarm_name          = "${local.name_prefix}-api-gateway-latency"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "Latency"
  namespace           = "AWS/ApiGateway"
  period              = "300"
  statistic           = "Average"
  threshold           = "2000"
  alarm_description   = "This metric monitors API Gateway latency"
  alarm_actions       = []
  
  dimensions = {
    ApiName = "${local.name_prefix}-rest-api"
  }
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-latency-alarm"
  })
}

# DynamoDB Throttling Alarm
resource "aws_cloudwatch_metric_alarm" "dynamodb_throttles" {
  alarm_name          = "${local.name_prefix}-dynamodb-throttles"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "ThrottledRequests"
  namespace           = "AWS/DynamoDB"
  period              = "300"
  statistic           = "Sum"
  threshold           = "0"
  alarm_description   = "This metric monitors DynamoDB throttling"
  alarm_actions       = []
  
  dimensions = {
    TableName = aws_dynamodb_table.users.name
  }
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-dynamodb-throttles-alarm"
  })
}