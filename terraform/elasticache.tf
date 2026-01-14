# AI Therapy Platform - ElastiCache Redis Configuration
# Breaking Barriers UK 2026 compliant Redis for LiveKit state management

# ElastiCache Subnet Group
resource "aws_elasticache_subnet_group" "livekit" {
  name       = "${local.name_prefix}-livekit-redis-subnet"
  subnet_ids = aws_subnet.private[*].id

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-livekit-redis-subnet"
    }
  )
}

# ElastiCache Redis Cluster
resource "aws_elasticache_cluster" "livekit" {
  cluster_id           = "${local.name_prefix}-livekit"
  engine               = "redis"
  engine_version       = "7.1"
  node_type            = "cache.t3.micro" # Small instance for hackathon
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  port                 = 6379
  subnet_group_name    = aws_elasticache_subnet_group.livekit.name
  security_group_ids   = [aws_security_group.redis.id]

  # Encryption at rest (Breaking Barriers UK 2026 requirement)
  # at_rest_encryption_enabled = var.enable_encryption

  # Encryption in transit (Breaking Barriers UK 2026 requirement)
  # transit_encryption_enabled = var.enable_encryption

  # Automatic backups
  snapshot_retention_limit = 1 # Minimal for hackathon
  snapshot_window          = "03:00-05:00"

  # Maintenance window
  maintenance_window = "sun:05:00-sun:07:00"

  # Auto minor version upgrade
  auto_minor_version_upgrade = true

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-livekit-redis"
    }
  )
}
