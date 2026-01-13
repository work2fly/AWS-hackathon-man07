# AI Therapy Platform - IAM Resources
# Breaking Barriers UK 2026 compliant IAM configuration

# Lambda Execution Role
resource "aws_iam_role" "lambda_execution_role" {
  name = "${local.name_prefix}-lambda-execution-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
  
  tags = local.common_tags
}

# Lambda Execution Policy
resource "aws_iam_policy" "lambda_execution_policy" {
  name        = "${local.name_prefix}-lambda-execution-policy"
  description = "IAM policy for AI Therapy Platform Lambda functions"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      # CloudWatch Logs
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:${local.region}:${local.account_id}:*"
      },
      # DynamoDB Access
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan",
          "dynamodb:BatchGetItem",
          "dynamodb:BatchWriteItem"
        ]
        Resource = [
          "arn:aws:dynamodb:${local.region}:${local.account_id}:table/${local.name_prefix}-*",
          "arn:aws:dynamodb:${local.region}:${local.account_id}:table/${local.name_prefix}-*/index/*"
        ]
      },
      # API Gateway Management
      {
        Effect = "Allow"
        Action = [
          "execute-api:ManageConnections"
        ]
        Resource = "arn:aws:execute-api:${local.region}:${local.account_id}:*"
      },
      # Cognito Access
      {
        Effect = "Allow"
        Action = [
          "cognito-idp:AdminCreateUser",
          "cognito-idp:AdminDeleteUser",
          "cognito-idp:AdminGetUser",
          "cognito-idp:AdminUpdateUserAttributes",
          "cognito-idp:AdminSetUserPassword",
          "cognito-idp:AdminConfirmSignUp",
          "cognito-idp:ListUsers"
        ]
        Resource = "arn:aws:cognito-idp:${local.region}:${local.account_id}:userpool/*"
      },
      # Bedrock Access (Breaking Barriers UK 2026 compliant)
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream",
          "bedrock:ListFoundationModels"
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "bedrock:modelId" = [
              "anthropic.claude-3-5-sonnet-20241022-v2:0",
              "anthropic.claude-3-opus-20240229",
              "amazon.nova-micro-v1:0",
              "amazon.nova-lite-v1:0",
              "amazon.nova-pro-v1:0",
              "meta.llama3-2-90b-instruct-v1:0",
              "mistral.pixtral-large-2411-v1:0",
              "stability.stable-image-ultra-v1:0"
            ]
          }
        }
      },
      # KMS Access
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt",
          "kms:GenerateDataKey",
          "kms:DescribeKey"
        ]
        Resource = "arn:aws:kms:${local.region}:${local.account_id}:key/*"
      },
      # X-Ray Tracing
      {
        Effect = "Allow"
        Action = [
          "xray:PutTraceSegments",
          "xray:PutTelemetryRecords"
        ]
        Resource = "*"
      }
    ]
  })
  
  tags = local.common_tags
}

# Attach policy to role
resource "aws_iam_role_policy_attachment" "lambda_execution_policy" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = aws_iam_policy.lambda_execution_policy.arn
}

# Attach AWS managed policy for basic Lambda execution
resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# API Gateway CloudWatch Role
resource "aws_iam_role" "api_gateway_cloudwatch_role" {
  name = "${local.name_prefix}-api-gateway-cloudwatch-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "apigateway.amazonaws.com"
        }
      }
    ]
  })
  
  tags = local.common_tags
}

# Attach CloudWatch policy to API Gateway role
resource "aws_iam_role_policy_attachment" "api_gateway_cloudwatch" {
  role       = aws_iam_role.api_gateway_cloudwatch_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonAPIGatewayPushToCloudWatchLogs"
}