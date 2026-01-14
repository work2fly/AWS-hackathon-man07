# AI Therapy Platform - Security Groups
# Breaking Barriers UK 2026 compliant security configuration

# Application Load Balancer Security Group
resource "aws_security_group" "alb" {
  name        = "${local.name_prefix}-alb-sg"
  description = "Security group for LiveKit Application Load Balancer"
  vpc_id      = aws_vpc.main.id

  # HTTP (for health checks and redirects)
  ingress {
    description = "HTTP from anywhere"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTPS (for secure connections)
  ingress {
    description = "HTTPS from anywhere"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # LiveKit HTTP port
  ingress {
    description = "LiveKit HTTP from anywhere"
    from_port   = 7880
    to_port     = 7880
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # LiveKit HTTPS port
  ingress {
    description = "LiveKit HTTPS from anywhere"
    from_port   = 7881
    to_port     = 7881
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-alb-sg"
    }
  )
}

# LiveKit ECS Tasks Security Group
resource "aws_security_group" "livekit_ecs" {
  name        = "${local.name_prefix}-livekit-ecs-sg"
  description = "Security group for LiveKit ECS tasks"
  vpc_id      = aws_vpc.main.id

  # LiveKit HTTP port from ALB
  ingress {
    description     = "LiveKit HTTP from ALB"
    from_port       = 7880
    to_port         = 7880
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  # LiveKit HTTPS port from ALB
  ingress {
    description     = "LiveKit HTTPS from ALB"
    from_port       = 7881
    to_port         = 7881
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  # WebRTC UDP port range (50000-60000)
  ingress {
    description = "WebRTC UDP from anywhere"
    from_port   = 50000
    to_port     = 60000
    protocol    = "udp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # WebRTC TCP port range (50000-60000) - fallback
  ingress {
    description = "WebRTC TCP from anywhere"
    from_port   = 50000
    to_port     = 60000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-livekit-ecs-sg"
    }
  )
}

# ElastiCache Redis Security Group
resource "aws_security_group" "redis" {
  name        = "${local.name_prefix}-redis-sg"
  description = "Security group for ElastiCache Redis"
  vpc_id      = aws_vpc.main.id

  # Redis port from LiveKit ECS tasks
  ingress {
    description     = "Redis from LiveKit ECS"
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.livekit_ecs.id]
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-redis-sg"
    }
  )
}
