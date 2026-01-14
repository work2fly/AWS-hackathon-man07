# AI Therapy Platform - ECS Configuration for LiveKit Server
# Breaking Barriers UK 2026 compliant ECS deployment

# ECS Cluster
resource "aws_ecs_cluster" "livekit" {
  name = "${local.name_prefix}-livekit-cluster"

  setting {
    name  = "containerInsights"
    value = var.enable_detailed_monitoring ? "enabled" : "disabled"
  }

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-livekit-cluster"
    }
  )
}

# CloudWatch Log Group for LiveKit
resource "aws_cloudwatch_log_group" "livekit" {
  name              = "/ecs/${local.name_prefix}-livekit"
  retention_in_days = var.log_retention_days

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-livekit-logs"
    }
  )
}

# ECS Task Execution Role
resource "aws_iam_role" "ecs_task_execution" {
  name = "${local.name_prefix}-ecs-task-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-ecs-task-execution-role"
    }
  )
}

# Attach AWS managed policy for ECS task execution
resource "aws_iam_role_policy_attachment" "ecs_task_execution" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Additional policy for Secrets Manager access
resource "aws_iam_role_policy" "ecs_secrets_access" {
  name = "${local.name_prefix}-ecs-secrets-access"
  role = aws_iam_role.ecs_task_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          aws_secretsmanager_secret.livekit_api_key.arn,
          aws_secretsmanager_secret.livekit_api_secret.arn
        ]
      }
    ]
  })
}

# ECS Task Role (for LiveKit container to access AWS services)
resource "aws_iam_role" "ecs_task" {
  name = "${local.name_prefix}-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-ecs-task-role"
    }
  )
}

# Policy for ECS task to access CloudWatch Logs
resource "aws_iam_role_policy" "ecs_task_cloudwatch" {
  name = "${local.name_prefix}-ecs-task-cloudwatch"
  role = aws_iam_role.ecs_task.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "${aws_cloudwatch_log_group.livekit.arn}:*"
      }
    ]
  })
}

# ECS Task Definition for LiveKit Server
resource "aws_ecs_task_definition" "livekit" {
  family                   = "${local.name_prefix}-livekit"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "1024"  # 1 vCPU
  memory                   = "2048"  # 2 GB RAM
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name      = "livekit"
      image     = "livekit/livekit-server:latest"
      essential = true

      portMappings = [
        {
          containerPort = 7880
          protocol      = "tcp"
          name          = "http"
        },
        {
          containerPort = 7881
          protocol      = "tcp"
          name          = "https"
        },
        {
          containerPort = 50000
          hostPort      = 60000
          protocol      = "udp"
          name          = "webrtc-udp"
        }
      ]

      environment = [
        {
          name  = "REDIS_HOST"
          value = aws_elasticache_replication_group.livekit.primary_endpoint_address
        },
        {
          name  = "REDIS_PORT"
          value = "6379"
        },
        {
          name  = "LIVEKIT_PORT"
          value = "7880"
        },
        {
          name  = "LIVEKIT_RTC_PORT_RANGE_START"
          value = "50000"
        },
        {
          name  = "LIVEKIT_RTC_PORT_RANGE_END"
          value = "60000"
        }
      ]

      secrets = [
        {
          name      = "LIVEKIT_KEYS"
          valueFrom = aws_secretsmanager_secret.livekit_api_key.arn
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.livekit.name
          "awslogs-region"        = local.region
          "awslogs-stream-prefix" = "livekit"
        }
      }

      healthCheck = {
        command     = ["CMD-SHELL", "wget --no-verbose --tries=1 --spider http://localhost:7880/ || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
    }
  ])

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-livekit-task"
    }
  )
}

# ECS Service for LiveKit
resource "aws_ecs_service" "livekit" {
  name            = "${local.name_prefix}-livekit-service"
  cluster         = aws_ecs_cluster.livekit.id
  task_definition = aws_ecs_task_definition.livekit.arn
  desired_count   = 1 # Start with 1 for hackathon
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.livekit_ecs.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.livekit_http.arn
    container_name   = "livekit"
    container_port   = 7880
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.livekit_https.arn
    container_name   = "livekit"
    container_port   = 7881
  }

  depends_on = [
    aws_lb_listener.livekit_http,
    aws_lb_listener.livekit_https
  ]

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-livekit-service"
    }
  )
}

# Auto Scaling Target
resource "aws_appautoscaling_target" "livekit" {
  max_capacity       = 4 # Max 4 tasks for hackathon
  min_capacity       = 1
  resource_id        = "service/${aws_ecs_cluster.livekit.name}/${aws_ecs_service.livekit.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

# Auto Scaling Policy - CPU based
resource "aws_appautoscaling_policy" "livekit_cpu" {
  name               = "${local.name_prefix}-livekit-cpu-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.livekit.resource_id
  scalable_dimension = aws_appautoscaling_target.livekit.scalable_dimension
  service_namespace  = aws_appautoscaling_target.livekit.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value = 70.0
  }
}

# Auto Scaling Policy - Memory based
resource "aws_appautoscaling_policy" "livekit_memory" {
  name               = "${local.name_prefix}-livekit-memory-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.livekit.resource_id
  scalable_dimension = aws_appautoscaling_target.livekit.scalable_dimension
  service_namespace  = aws_appautoscaling_target.livekit.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageMemoryUtilization"
    }
    target_value = 80.0
  }
}
