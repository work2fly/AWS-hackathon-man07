# Lambda Deployment Guide
🏆 Breaking Barriers UK 2026 compliant

## Quick Start

To recreate the Lambda ZIP files with all the new red flag detection services:

### Option 1: Python Script (Recommended)
```bash
cd backend
python scripts/package_lambdas.py
```

### Option 2: Bash Script
```bash
cd backend
./scripts/package-lambdas.sh
```

## What Gets Packaged

Each Lambda function ZIP file includes:

### Core Lambda Handler
- The specific handler file (e.g., `auth_handlers.py`, `session_handlers.py`)

### All Service Modules
- ✅ **red_flag_detection_service.py** - UKind charity pattern detection
- ✅ **notification_service.py** - Multi-channel notifications
- ✅ **red_flag_management_service.py** - Case management workflows  
- ✅ **trauma_informed_response_service.py** - UKind trauma-informed responses
- Plus all existing services (user, session, auth, etc.)

### Supporting Modules
- `data/` - Repository classes for DynamoDB access
- `models/` - Pydantic models and enums
- `utils/` - Logging, validation, encryption utilities
- `config/` - Configuration management
- `middleware/` - Authentication and security middleware

### Dependencies
- Optimized for Lambda (development dependencies excluded)
- Uses `requirements-lambda.txt` for smaller package sizes

### Automatic Terraform Integration
- ✅ **ZIP files automatically copied to `terraform/` directory**
- ✅ **Ready for immediate `terraform apply`**
- ✅ **No manual file copying required**

## Package Sizes

The script monitors package sizes and warns if approaching Lambda limits:
- **10MB zipped**: Limit for console editing capability
- **50MB unzipped**: Hard Lambda limit

## Deployment Options

### 1. Terraform (Recommended - Fully Automated)
```bash
# Package and deploy in one go
cd backend
python scripts/package_lambdas.py
cd ../terraform
terraform apply
```

The packaging script automatically:
- ✅ Creates ZIP files in `backend/dist/`
- ✅ Copies ZIP files to `terraform/` directory
- ✅ Makes them ready for immediate Terraform deployment

### 2. AWS CLI
```bash
# Update a specific function (from terraform directory)
aws lambda update-function-code \
  --function-name ai-therapy-auth-handler \
  --zip-file fileb://auth_handlers.zip

# Update all functions
for func in auth_handlers cognito_triggers protected_endpoints session_handlers websocket_handlers; do
  aws lambda update-function-code \
    --function-name ai-therapy-${func//_/-} \
    --zip-file fileb://${func}.zip
done
```

### 3. AWS Console
1. Navigate to Lambda service in AWS Console
2. Select your function
3. Go to "Code" tab
4. Click "Upload from" → ".zip file"
5. Select the appropriate ZIP file from `terraform/` directory

## New Services Integration

All Lambda packages now include the comprehensive red flag detection system:

### Red Flag Detection
- Real-time content analysis for safety triggers
- UKind charity validated patterns for:
  - Suicidal ideation
  - Self-harm indicators
  - Abuse scenarios
  - Violence threats
  - Crisis situations

### Trauma-Informed Responses
- UKind charity guidelines implementation
- UK-specific mental health resources
- Grounding techniques for crisis situations
- Response safety validation

### Notification System
- Multi-channel alerts (email, SMS, in-app)
- Escalation logic for severe cases
- Therapist and admin notifications

### Case Management
- Red flag tracking and resolution
- Audit trails for compliance
- Analytics and reporting

## Important Notes

⚠️ **Breaking Barriers UK 2026 Constraints:**
- AWS accounts terminate at **23:00 on 15th January 2026**
- Save all work to Git repositories before deadline
- Only use permitted AWS services and regions (us-west-2, us-east-1)

🔒 **Security:**
- All packages include encryption and security utilities
- No PII or sensitive data in package contents
- Follows AWS Lambda security best practices

📦 **Package Management:**
- Packages are optimized for size and performance
- Development dependencies excluded from Lambda packages
- All necessary dependencies included for runtime

## Troubleshooting

### Package Too Large
If packages exceed size limits:
1. Check for unnecessary dependencies in `requirements-lambda.txt`
2. Remove unused service modules from packaging script
3. Use Lambda layers for common dependencies

### Import Errors
If you encounter import errors after deployment:
1. Verify all `__init__.py` files are created
2. Check relative import paths in service modules
3. Ensure all dependencies are included in package

### Missing Dependencies
If Lambda functions fail due to missing modules:
1. Add missing dependencies to `requirements-lambda.txt`
2. Rerun packaging script
3. Redeploy updated ZIP files

## Support

For deployment issues during the hackathon, contact Environment Leads:
- **London**: Mevlit (mevlit@), Rama (ramaknat@)
- **Manchester**: Basheer Ahmed (basheerz@), Robert Bradley (rbradaws@)
- **Dublin**: Shane Adams (shaadas@), Sherin Chandy (chandys@), Eduarda Siqueira (edds@)