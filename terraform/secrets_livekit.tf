# AI Therapy Platform - Secrets Manager for LiveKit
# Breaking Barriers UK 2026 compliant secrets management

# Random API Key and Secret generation
resource "random_password" "livekit_api_key" {
  length  = 32
  special = false
}

resource "random_password" "livekit_api_secret" {
  length  = 64
  special = true
}

# Secrets Manager - LiveKit API Key
resource "aws_secretsmanager_secret" "livekit_api_key" {
  name        = "${local.name_prefix}-livekit-api-key"
  description = "LiveKit API Key for authentication (format: key:secret)"

  recovery_window_in_days = 0 # Immediate deletion for hackathon

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-livekit-api-key"
    }
  )
}

# Store in format "key: secret" as LiveKit expects
resource "aws_secretsmanager_secret_version" "livekit_api_key" {
  secret_id     = aws_secretsmanager_secret.livekit_api_key.id
  secret_string = "${random_password.livekit_api_key.result}: ${random_password.livekit_api_secret.result}"
}

# Secrets Manager - LiveKit API Secret (separate for Lambda usage)
resource "aws_secretsmanager_secret" "livekit_api_secret" {
  name        = "${local.name_prefix}-livekit-api-secret"
  description = "LiveKit API Secret for authentication"

  recovery_window_in_days = 0 # Immediate deletion for hackathon

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-livekit-api-secret"
    }
  )
}

resource "aws_secretsmanager_secret_version" "livekit_api_secret" {
  secret_id     = aws_secretsmanager_secret.livekit_api_secret.id
  secret_string = random_password.livekit_api_secret.result
}

# Secrets Manager - LiveKit API Key (separate for Lambda usage)
resource "aws_secretsmanager_secret" "livekit_key_only" {
  name        = "${local.name_prefix}-livekit-key-only"
  description = "LiveKit API Key only (for Lambda token generation)"

  recovery_window_in_days = 0 # Immediate deletion for hackathon

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-livekit-key-only"
    }
  )
}

resource "aws_secretsmanager_secret_version" "livekit_key_only" {
  secret_id     = aws_secretsmanager_secret.livekit_key_only.id
  secret_string = random_password.livekit_api_key.result
}
