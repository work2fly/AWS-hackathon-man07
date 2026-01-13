# AI Therapy Platform - Main Terraform Configuration
# Breaking Barriers UK 2026 compliant infrastructure

terraform {
  required_version = ">= 1.12"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.100"
    }
  }
  
  # S3 backend configuration is loaded from backend.hcl
  # Run: terraform init -backend-config=backend.hcl
  backend "s3" {}
}

# AWS Provider configuration
provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "ai-therapy-platform"
      Environment = var.environment
      Team        = "backend"
      Event       = "breaking-barriers-uk-2026"
      ManagedBy   = "terraform"
    }
  }
}

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# Local values
locals {
  account_id = data.aws_caller_identity.current.account_id
  region     = data.aws_region.current.name
  
  # Resource naming convention
  name_prefix = "${var.project_name}-${var.environment}"
  
  # Common tags
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    Team        = "backend"
    Event       = "breaking-barriers-uk-2026"
    ManagedBy   = "terraform"
  }
}