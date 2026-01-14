"""
AWS Configuration for AI Therapy Platform
Handles AWS service clients and configuration
🏆 Breaking Barriers UK 2026 compliant
"""

import boto3
import os
from typing import Optional
from botocore.config import Config

# AWS Configuration
AWS_REGION = os.getenv('AWS_DEFAULT_REGION', 'us-west-2')
AWS_ACCOUNT_ID = os.getenv('AWS_ACCOUNT_ID')

# Service configuration
RETRY_CONFIG = Config(
    region_name=AWS_REGION,
    retries={
        'max_attempts': 3,
        'mode': 'adaptive'
    }
)

class AWSClients:
    """Centralized AWS client management"""
    
    def __init__(self):
        self._dynamodb = None
        self._cognito_idp = None
        self._apigateway = None
        self._bedrock = None
        self._bedrock_runtime = None
        self._lambda_client = None
        self._cloudwatch = None
    
    @property
    def dynamodb(self):
        """DynamoDB client for data operations"""
        if self._dynamodb is None:
            self._dynamodb = boto3.client('dynamodb', config=RETRY_CONFIG)
        return self._dynamodb
    
    @property
    def dynamodb_resource(self):
        """DynamoDB resource for higher-level operations"""
        return boto3.resource('dynamodb', config=RETRY_CONFIG)
    
    @property
    def cognito_idp(self):
        """Cognito Identity Provider client"""
        if self._cognito_idp is None:
            self._cognito_idp = boto3.client('cognito-idp', config=RETRY_CONFIG)
        return self._cognito_idp
    
    @property
    def apigateway(self):
        """API Gateway Management client"""
        if self._apigateway is None:
            self._apigateway = boto3.client('apigatewaymanagementapi', config=RETRY_CONFIG)
        return self._apigateway
    
    @property
    def bedrock(self):
        """Amazon Bedrock client for AI services"""
        if self._bedrock is None:
            self._bedrock = boto3.client('bedrock', config=RETRY_CONFIG)
        return self._bedrock
    
    @property
    def bedrock_runtime(self):
        """Amazon Bedrock Runtime client for inference"""
        if self._bedrock_runtime is None:
            self._bedrock_runtime = boto3.client('bedrock-runtime', config=RETRY_CONFIG)
        return self._bedrock_runtime
    
    @property
    def lambda_client(self):
        """AWS Lambda client"""
        if self._lambda_client is None:
            self._lambda_client = boto3.client('lambda', config=RETRY_CONFIG)
        return self._lambda_client
    
    @property
    def cloudwatch(self):
        """CloudWatch client for logging and monitoring"""
        if self._cloudwatch is None:
            self._cloudwatch = boto3.client('cloudwatch', config=RETRY_CONFIG)
        return self._cloudwatch

# Global AWS clients instance
aws_clients = AWSClients()

def get_account_id() -> Optional[str]:
    """Get AWS account ID from STS"""
    try:
        sts = boto3.client('sts', config=RETRY_CONFIG)
        return sts.get_caller_identity()['Account']
    except Exception as e:
        print(f"Error getting account ID: {e}")
        return None

def get_aws_config() -> dict:
    """Get AWS configuration dictionary"""
    return {
        'region': AWS_REGION,
        'account_id': AWS_ACCOUNT_ID or get_account_id(),
        'retry_config': RETRY_CONFIG
    }