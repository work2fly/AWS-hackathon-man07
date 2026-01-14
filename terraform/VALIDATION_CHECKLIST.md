# LiveKit Infrastructure Validation Checklist
🏆 Breaking Barriers UK 2026 Hackathon

## Pre-Deployment Validation

### 1. Terraform Configuration
- [ ] Run `terraform fmt -recursive` to format all files
- [ ] Run `terraform validate` to check syntax
- [ ] Review `terraform plan` output for expected resources
- [ ] Verify all resource names follow naming convention
- [ ] Check that region is set to `us-west-2`

### 2. AWS Prerequisites
- [ ] AWS CLI configured with valid credentials
- [ ] Access to us-west-2 region confirmed
- [ ] IAM permissions for required services verified
- [ ] S3 backend bucket exists (if using remote state)

### 3. Configuration Review
- [ ] `terraform.tfvars` configured correctly
- [ ] `enable_encryption = true` for security
- [ ] `enable_deletion_protection = false` for easy cleanup
- [ ] Resource limits appropriate for hackathon

## Post-Deployment Validation

### 1. VPC and Networking
- [ ] VPC created with correct CIDR (10.0.0.0/16)
- [ ] 2 public subnets created
- [ ] 2 private subnets created
- [ ] Internet Gateway attached
- [ ] 2 NAT Gateways provisioned
- [ ] Route tables configured correctly
- [ ] S3 VPC endpoint created

### 2. Security Groups
- [ ] ALB security group allows ports 80, 443, 7880, 7881
- [ ] ECS security group allows ports 7880, 7881, 50000-60000
- [ ] Redis security group allows port 6379 from ECS only
- [ ] All security groups have proper egress rules

### 3. ElastiCache Redis
- [ ] Redis cluster created (cache.t3.micro)
- [ ] Deployed in private subnets
- [ ] Encryption at rest enabled
- [ ] Encryption in transit enabled
- [ ] Subnet group configured
- [ ] Security group attached

### 4. ECS Cluster and Service
- [ ] ECS cluster created
- [ ] Task definition registered
- [ ] Container image: livekit/livekit-server:latest
- [ ] CPU: 1024 (1 vCPU)
- [ ] Memory: 2048 (2 GB)
- [ ] Port mappings: 7880, 7881, 50000-60000
- [ ] Environment variables set correctly
- [ ] Secrets configured from Secrets Manager
- [ ] Health check configured
- [ ] CloudWatch logging enabled
- [ ] ECS service created
- [ ] Service running in private subnets
- [ ] Desired count: 1
- [ ] Running count: 1
- [ ] Service status: ACTIVE

### 5. Load Balancers
- [ ] Application Load Balancer created
- [ ] ALB in public subnets
- [ ] ALB security group attached
- [ ] HTTP listener (7880) configured
- [ ] HTTPS listener (7881) configured
- [ ] Target groups created
- [ ] Health checks configured
- [ ] Network Load Balancer created
- [ ] NLB UDP listener (50000) configured
- [ ] Targets registered and healthy

### 6. Secrets Manager
- [ ] LiveKit API key secret created
- [ ] LiveKit API secret created
- [ ] Combined secret created (key:secret format)
- [ ] Secrets accessible by ECS task execution role
- [ ] Secret values generated correctly

### 7. DynamoDB
- [ ] LiveKitRooms table created
- [ ] Partition key: roomName
- [ ] GSI: SessionIndex configured
- [ ] GSI: ClientIndex configured
- [ ] TTL enabled on ttl attribute
- [ ] Encryption at rest enabled
- [ ] Point-in-time recovery enabled

### 8. IAM Roles and Policies
- [ ] ECS task execution role created
- [ ] ECS task role created
- [ ] Secrets Manager access policy attached
- [ ] CloudWatch Logs policy attached
- [ ] Roles have correct trust relationships

### 9. CloudWatch
- [ ] Log group created: /ecs/ai-therapy-platform-dev-livekit
- [ ] Log retention set to 7 days
- [ ] Container Insights enabled (if configured)
- [ ] Logs appearing from ECS tasks

### 10. Auto-Scaling
- [ ] Auto-scaling target created
- [ ] CPU-based scaling policy configured (70%)
- [ ] Memory-based scaling policy configured (80%)
- [ ] Min capacity: 1
- [ ] Max capacity: 4

## Functional Testing

### 1. Connectivity Tests
- [ ] Run `./test-livekit-connectivity.sh` successfully
- [ ] ALB reachable on port 7880
- [ ] ECS service shows healthy status
- [ ] Target groups show healthy targets
- [ ] Redis endpoint accessible from ECS
- [ ] Secrets Manager accessible
- [ ] CloudWatch logs showing activity

### 2. Token Generation Tests
- [ ] Install livekit-api package
- [ ] Run `test-livekit-token.py` successfully
- [ ] Token generated without errors
- [ ] Token validates correctly
- [ ] Token contains correct grants

### 3. Health Checks
- [ ] ALB health checks passing
- [ ] ECS task health checks passing
- [ ] Target group health checks passing
- [ ] No error logs in CloudWatch

### 4. Manual Verification
- [ ] Curl ALB endpoint returns response
- [ ] ECS tasks not restarting
- [ ] No errors in CloudWatch Logs
- [ ] Redis connection successful (check logs)

## Security Validation

### 1. Encryption
- [ ] DynamoDB encryption at rest enabled
- [ ] ElastiCache encryption at rest enabled
- [ ] ElastiCache encryption in transit enabled
- [ ] Secrets stored in Secrets Manager
- [ ] TLS for all external connections

### 2. Network Security
- [ ] ECS tasks in private subnets
- [ ] Redis in private subnets
- [ ] No public IPs on ECS tasks
- [ ] Security groups follow least privilege
- [ ] Only required ports open

### 3. IAM Security
- [ ] Roles follow least privilege principle
- [ ] No overly permissive policies
- [ ] Trust relationships correctly configured
- [ ] No hardcoded credentials

## Performance Validation

### 1. Resource Utilization
- [ ] ECS task CPU < 50% at idle
- [ ] ECS task memory < 50% at idle
- [ ] Redis CPU < 30% at idle
- [ ] No throttling errors

### 2. Latency
- [ ] ALB response time < 100ms
- [ ] Health check response time < 5s
- [ ] Token generation < 1s

## Cost Validation

### 1. Resource Sizing
- [ ] ECS task size appropriate (1 vCPU, 2GB)
- [ ] Redis instance appropriate (cache.t3.micro)
- [ ] NAT Gateways necessary (2 for HA)
- [ ] Log retention appropriate (7 days)

### 2. Cost Monitoring
- [ ] Estimated daily cost ~$5.50
- [ ] No unexpected resources created
- [ ] Auto-scaling limits set correctly

## Breaking Barriers UK 2026 Compliance

### 1. Region Compliance
- [ ] All resources in us-west-2
- [ ] No resources in other regions

### 2. Service Compliance
- [ ] Only permitted services used
- [ ] No blocked services used
- [ ] No prohibited instance types

### 3. Security Compliance
- [ ] Encryption enabled everywhere
- [ ] No PII in logs or configs
- [ ] Secure credential management

## Documentation Validation

### 1. Files Created
- [ ] vpc.tf
- [ ] security_groups.tf
- [ ] elasticache.tf
- [ ] ecs_livekit.tf
- [ ] alb_livekit.tf
- [ ] secrets_livekit.tf
- [ ] dynamodb.tf (updated)
- [ ] outputs.tf (updated)
- [ ] livekit.yaml
- [ ] LIVEKIT_DEPLOYMENT.md
- [ ] LIVEKIT_TESTING.md
- [ ] test-livekit-connectivity.sh
- [ ] test-livekit-token.py

### 2. Documentation Quality
- [ ] Deployment guide complete
- [ ] Testing guide complete
- [ ] Troubleshooting section included
- [ ] Code examples provided
- [ ] Architecture diagrams clear

## Sign-Off

### Pre-Deployment
- [ ] All pre-deployment checks passed
- [ ] Configuration reviewed and approved
- [ ] Ready to deploy

**Signed**: _________________ **Date**: _________________

### Post-Deployment
- [ ] All post-deployment checks passed
- [ ] Functional tests passed
- [ ] Security validation passed
- [ ] Ready for integration

**Signed**: _________________ **Date**: _________________

## Notes

Use this space to document any issues, deviations, or special configurations:

---

---

---

## Next Steps After Validation

1. Proceed to Task 2: Implement LiveKit Agent with Nova Sonic
2. Integrate with Lambda functions for token generation
3. Connect frontend React application
4. Test end-to-end therapy session flow

---

🏆 **Breaking Barriers UK 2026 Compliant**
