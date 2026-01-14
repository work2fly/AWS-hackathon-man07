# AI Therapy Platform - Application Load Balancer for LiveKit
# Breaking Barriers UK 2026 compliant ALB configuration

# Application Load Balancer
resource "aws_lb" "livekit" {
  name               = "${local.name_prefix}-lk-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id

  enable_deletion_protection = var.enable_deletion_protection
  enable_http2              = true
  enable_cross_zone_load_balancing = true

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-livekit-alb"
    }
  )
}

# Target Group for LiveKit HTTP (7880)
resource "aws_lb_target_group" "livekit_http" {
  name        = "${local.name_prefix}-lk-http"
  port        = 7880
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
    path                = "/health"
    protocol            = "HTTP"
    matcher             = "200"
  }

  deregistration_delay = 30

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-lk-http-tg"
    }
  )
}

# Target Group for LiveKit HTTPS (7881)
resource "aws_lb_target_group" "livekit_https" {
  name        = "${local.name_prefix}-lk-https"
  port        = 7881
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
    path                = "/health"
    protocol            = "HTTP"
    matcher             = "200"
  }

  deregistration_delay = 30

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-lk-https-tg"
    }
  )
}

# ALB Listener for HTTP (7880)
resource "aws_lb_listener" "livekit_http" {
  load_balancer_arn = aws_lb.livekit.arn
  port              = "7880"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.livekit_http.arn
  }

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-livekit-http-listener"
    }
  )
}

# ALB Listener for HTTPS (7881)
resource "aws_lb_listener" "livekit_https" {
  load_balancer_arn = aws_lb.livekit.arn
  port              = "7881"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.livekit_https.arn
  }

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-livekit-https-listener"
    }
  )
}

# Network Load Balancer for WebRTC UDP traffic
resource "aws_lb" "livekit_webrtc" {
  name               = "${local.name_prefix}-lk-nlb"
  internal           = false
  load_balancer_type = "network"
  subnets            = aws_subnet.public[*].id

  enable_deletion_protection       = var.enable_deletion_protection
  enable_cross_zone_load_balancing = true

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-livekit-webrtc-nlb"
    }
  )
}

# Target Group for WebRTC UDP
resource "aws_lb_target_group" "livekit_webrtc_udp" {
  name        = "${local.name_prefix}-lk-udp"
  port        = 50000
  protocol    = "UDP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 10
    interval            = 30
    protocol            = "TCP"
    port                = "7880"
  }

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-livekit-webrtc-udp-tg"
    }
  )
}

# NLB Listener for WebRTC UDP
resource "aws_lb_listener" "livekit_webrtc_udp" {
  load_balancer_arn = aws_lb.livekit_webrtc.arn
  port              = "50000"
  protocol          = "UDP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.livekit_webrtc_udp.arn
  }

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-livekit-webrtc-udp-listener"
    }
  )
}
