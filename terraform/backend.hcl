# Terraform S3 Backend Configuration
# 🏆 Breaking Barriers UK 2026 compliant

bucket         = "ai-therapy-platform-terraform-state"
key            = "dev/terraform.tfstate"
region         = "us-west-2"
encrypt        = true
dynamodb_table = "ai-therapy-platform-terraform-locks"

# Optional: Enable state locking and consistency checking
# This requires the DynamoDB table to exist