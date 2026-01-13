---
inclusion: always
---

# Breaking Barriers UK 2026 - Q Developer Rules

## Purpose
These rules ensure all teams follow the AWS Breaking Barriers UK 2026 hackathon constraints, security requirements, and best practices when using Amazon Q Developer during the event.

## Instructions

### AWS Account & Environment Constraints
- **CRITICAL**: Only use AWS regions `us-west-2` (Oregon) and `us-east-1` (for global services only)
- **CRITICAL**: All AWS accounts terminate at 23:00 on 15th January 2026 - ensure all code is saved to Git repositories or locally before this time
- **CRITICAL**: Maximum 10 participants per team (hard Workshop Studio limit)
- When suggesting AWS services, ALWAYS verify they are in the permitted services list below
- When recommending EC2 instances, NEVER suggest `*6xlarge`, `*8xlarge`, `*10xlarge`, `*12xlarge`, `*16xlarge`, `*18xlarge`, `*24xlarge`, `f1.4xlarge`, `x1*`, `z1*`, or `*metal` instances
- Always remind users that Workshop Studio has specific quota restrictions on certain EC2 instance types

### Data Security & Compliance Requirements
- **CRITICAL**: NEVER process, store, or suggest handling any of the following data types:
  - Personal data or PII
  - Regulated data
  - Financial information
  - Information about race, ethnic origin, political opinions, religious views, trade union memberships
  - Genetic data, biometric data, health data
  - Payment processing data
  - Malicious code or malware
- When suggesting data examples, always use generic placeholders like `[name]`, `[email]`, `[phone_number]`, `[address]`
- Always recommend encryption for data at rest and in transit

### Bedrock Model Restrictions
- **CRITICAL**: Only use these permitted Bedrock models:
  - All Amazon Models
  - Anthropic Claude Sonnet 4.5
  - Anthropic Claude Opus 4.5
  - Meta Llama 4 Maverick 17B Instruct (Georestricted)
  - Mistral Pixtral Large (25.02)
  - Stable Diffusion 3.5 Large
- **CRITICAL**: Design solutions to stay below 1 Request per Second (RPS/TPS) to avoid throttling
- When suggesting Bedrock usage, always include rate limiting considerations
- NEVER suggest using blocked Bedrock models (ai21, cohere, deepseek, google, luma, nvidia, openai, qwen, etc.)

### Permitted AWS Services
When recommending AWS services, ensure they are from this approved list:
- **Compute**: EC2, Lambda, ECS, EKS, Auto Scaling
- **Storage**: S3, S3 Tables, S3 Vectors, S3 Object Lambda
- **Database**: DynamoDB, RDS, RDS Data API, Redshift, Redshift Serverless, Neptune, ElastiCache, MemoryDB
- **AI/ML**: Bedrock, Bedrock Agent Core, SageMaker, Comprehend, Textract, Transcribe, Translate, Personalize, Kendra
- **Analytics**: Athena, Glue, Kinesis, Data Firehose, QuickSight
- **Networking**: API Gateway, CloudFront, Route 53, VPC (via EC2), Elastic Load Balancing
- **Security**: IAM, KMS, Secrets Manager, WAF v2, Cognito
- **Monitoring**: CloudWatch, CloudTrail, X-Ray, CloudWatch Synthetics
- **Integration**: SNS, SQS, EventBridge, Step Functions, EventBridge Pipes, EventBridge Scheduler
- **Developer Tools**: CodeBuild, CodeCommit, CodeDeploy, CodePipeline, Cloud9 (blocked by Workshop Studio), CloudShell
- **Management**: CloudFormation, SSM, Cost Explorer, Service Quotas, Resource Groups
- **Other**: Amplify, Q Developer, Q Business, Q Apps, Application Auto Scaling

### Blocked Services & Actions
- **NEVER** suggest purchasing reservations, savings plans, or capacity blocks
- **NEVER** suggest Route 53 domain purchases (all domain API calls blocked)
- **NEVER** suggest Cloud9 (blocked by Workshop Studio despite IAM permissions)
- **NEVER** suggest services not in the permitted list above
- Be aware that some services have specific blocked actions - refer to the detailed restrictions when needed

### Development Environment Guidelines
- The provided VS Code environment includes: AWS CLI, Git, Node, AWS CDK, Kiro CLI, uv, Python, Java, Go, .NET, Rust, Docker, Terraform, Q Developer
- When multiple team members use the same VS Code instance, recommend using different files/folders to avoid conflicts
- Always suggest saving work to Git repositories regularly due to account termination deadline
- Recommend local development setup as an alternative to the provided VS Code environment

### Architecture & Security Best Practices
- Always recommend encryption for S3 buckets, DynamoDB tables, SNS topics, and SQS queues
- Always suggest enforcing SSL/TLS for data in transit
- Always recommend blocking public access for S3 buckets unless specifically required
- When designing solutions, prioritize serverless and managed services to reduce operational overhead
- Always include monitoring and logging in architectural recommendations
- Suggest using CloudWatch for metrics, alarms, and dashboards
- Recommend implementing proper error handling and retry logic

### Cost Optimization
- Always suggest using appropriate instance sizes (avoid oversizing)
- Recommend using spot instances for non-critical workloads when appropriate
- Suggest implementing auto-scaling to optimize costs
- Always mention staying within free tier limits when possible
- Recommend monitoring costs using Cost Explorer

### Team Collaboration
- Always recommend using Git for version control and collaboration
- Suggest clear naming conventions for AWS resources
- Recommend using CloudFormation or CDK for infrastructure as code
- Suggest implementing proper tagging strategies for resource management
- Always recommend documenting architecture decisions and setup instructions

### Emergency Contacts
When teams encounter issues, direct them to these Environment Leads:
- **London**: Mevlit (mevlit@), Rama (ramaknat@)
- **Manchester**: Basheer Ahmed (basheerz@), Robert Bradley (rbradaws@)
- **Dublin**: Shane Adams (shaadas@), Sherin Chandy (chandys@), Eduarda Siqueira (edds@)

## Priority
Critical

## Error Handling
- If suggesting a service not in the permitted list, immediately correct and provide an alternative from the approved services
- If asked about blocked data types, refuse and explain the security requirements
- If unsure about service permissions, recommend checking with Environment Leads
- If suggesting architecture that might exceed rate limits, always include throttling and retry mechanisms
- When in doubt about compliance, err on the side of caution and suggest the most secure approach

## Acknowledgment Behavior
- When following these rules, include "🏆 Breaking Barriers UK 2026 compliant" in responses
- When correcting non-compliant suggestions, include "⚠️ Adjusted for hackathon constraints"
- When suggesting alternatives for blocked services, include "✅ Alternative solution provided"

## Additional Notes
- This is for the AWS Breaking Barriers Challenge 2026 hackathon only
- All information is for internal use - be mindful when sharing with participants
- Workshop Studio Event: https://catalog.workshops.aws/genai-hackathon (for reference only)
- Account access codes should only be distributed after the Environment Presentation
- Remember: accounts terminate at 23:00 on 15th January 2026 - save all work before this deadline!