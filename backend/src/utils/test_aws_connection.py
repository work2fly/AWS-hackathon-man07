#!/usr/bin/env python3
"""
Test AWS connection and configuration
Validates AWS credentials and service access
"""

import boto3
import os
import sys
from botocore.exceptions import ClientError, NoCredentialsError
from config.aws_config import aws_clients, get_account_id

def test_aws_credentials():
    """Test AWS credentials and basic access"""
    print("🔍 Testing AWS credentials...")
    
    try:
        # Test STS access
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        
        print(f"✅ AWS credentials valid")
        print(f"   Account ID: {identity['Account']}")
        print(f"   User ARN: {identity['Arn']}")
        print(f"   Region: {os.getenv('AWS_DEFAULT_REGION', 'Not set')}")
        
        return True
        
    except NoCredentialsError:
        print("❌ AWS credentials not found")
        print("   Please set AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and AWS_SESSION_TOKEN")
        return False
        
    except ClientError as e:
        print(f"❌ AWS credentials error: {e}")
        return False

def test_service_access():
    """Test access to required AWS services"""
    print("\n🔍 Testing AWS service access...")
    
    services_to_test = [
        ('DynamoDB', lambda: aws_clients.dynamodb.list_tables()),
        ('Cognito', lambda: aws_clients.cognito_idp.list_user_pools(MaxResults=1)),
        ('Bedrock', lambda: aws_clients.bedrock.list_foundation_models()),
        ('Lambda', lambda: aws_clients.lambda_client.list_functions(MaxItems=1)),
        ('CloudWatch', lambda: aws_clients.cloudwatch.list_metrics(MaxRecords=1))
    ]
    
    results = {}
    
    for service_name, test_func in services_to_test:
        try:
            test_func()
            print(f"✅ {service_name} access: OK")
            results[service_name] = True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['AccessDenied', 'UnauthorizedOperation']:
                print(f"⚠️  {service_name} access: Limited permissions ({error_code})")
                results[service_name] = 'limited'
            else:
                print(f"❌ {service_name} access: Error ({error_code})")
                results[service_name] = False
        except Exception as e:
            print(f"❌ {service_name} access: Unexpected error ({str(e)})")
            results[service_name] = False
    
    return results

def test_bedrock_models():
    """Test access to Breaking Barriers UK 2026 compliant Bedrock models"""
    print("\n🔍 Testing Bedrock model access...")
    
    # Breaking Barriers UK 2026 compliant models
    permitted_models = [
        'anthropic.claude-3-5-sonnet-20241022-v2:0',
        'anthropic.claude-3-opus-20240229',
        'amazon.nova-micro-v1:0',
        'amazon.nova-lite-v1:0',
        'amazon.nova-pro-v1:0'
    ]
    
    try:
        response = aws_clients.bedrock.list_foundation_models()
        available_models = [model['modelId'] for model in response['modelSummaries']]
        
        print("🏆 Breaking Barriers UK 2026 compliant models:")
        for model in permitted_models:
            if model in available_models:
                print(f"✅ {model}: Available")
            else:
                print(f"⚠️  {model}: Not available in this region")
                
    except Exception as e:
        print(f"❌ Error checking Bedrock models: {e}")

def main():
    """Main test function"""
    print("🚀 AI Therapy Platform - AWS Configuration Test")
    print("=" * 50)
    
    # Test credentials
    if not test_aws_credentials():
        sys.exit(1)
    
    # Test service access
    service_results = test_service_access()
    
    # Test Bedrock models
    test_bedrock_models()
    
    # Summary
    print("\n📊 Test Summary:")
    print("=" * 30)
    
    working_services = sum(1 for result in service_results.values() if result is True)
    limited_services = sum(1 for result in service_results.values() if result == 'limited')
    failed_services = sum(1 for result in service_results.values() if result is False)
    
    print(f"✅ Working services: {working_services}")
    print(f"⚠️  Limited access: {limited_services}")
    print(f"❌ Failed services: {failed_services}")
    
    if failed_services == 0:
        print("\n🎉 All tests passed! AWS configuration is ready.")
        return 0
    else:
        print(f"\n⚠️  Some services have issues. Check permissions and try again.")
        return 1

if __name__ == "__main__":
    sys.exit(main())