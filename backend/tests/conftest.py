#!/usr/bin/env python3
"""
Pytest configuration for AI Therapy Platform backend tests
🏆 Breaking Barriers UK 2026 compliant
"""

import sys
import os
from unittest.mock import Mock, MagicMock, patch

# Get the backend directory path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Set up environment variables for testing BEFORE any imports
os.environ.setdefault('AWS_DEFAULT_REGION', 'us-west-2')
os.environ.setdefault('COGNITO_USER_POOL_ID', 'us-west-2_TestPool123')
os.environ.setdefault('COGNITO_CLIENT_ID', 'test-client-id-123')
os.environ.setdefault('COGNITO_CLIENT_SECRET', 'test-client-secret')
os.environ.setdefault('DYNAMODB_USERS_TABLE', 'test-users-table')
os.environ.setdefault('DYNAMODB_SESSIONS_TABLE', 'test-sessions-table')
os.environ.setdefault('DYNAMODB_RED_FLAGS_TABLE', 'test-red-flags-table')
os.environ.setdefault('DYNAMODB_NOTIFICATIONS_TABLE', 'test-notifications-table')
os.environ.setdefault('DYNAMODB_CONNECTIONS_TABLE', 'test-connections-table')
os.environ.setdefault('SNS_TOPIC_ARN', 'arn:aws:sns:us-west-2:123456789012:test-topic')
os.environ.setdefault('ENVIRONMENT', 'test')

# Pytest fixtures
import pytest

@pytest.fixture(autouse=True)
def mock_aws_services():
    """Mock AWS services for all tests"""
    with patch('boto3.client') as mock_client, \
         patch('boto3.resource') as mock_resource:
        # Configure mock clients
        mock_dynamodb = MagicMock()
        mock_cognito = MagicMock()
        mock_cloudwatch = MagicMock()
        mock_sns = MagicMock()
        mock_ses = MagicMock()
        mock_s3 = MagicMock()
        mock_api_gateway = MagicMock()
        
        def get_mock_client(service_name, **kwargs):
            clients = {
                'dynamodb': mock_dynamodb,
                'cognito-idp': mock_cognito,
                'cloudwatch': mock_cloudwatch,
                'sns': mock_sns,
                'ses': mock_ses,
                's3': mock_s3,
                'apigatewaymanagementapi': mock_api_gateway
            }
            return clients.get(service_name, MagicMock())
        
        mock_client.side_effect = get_mock_client
        mock_resource.return_value = MagicMock()
        
        yield {
            'dynamodb': mock_dynamodb,
            'cognito': mock_cognito,
            'cloudwatch': mock_cloudwatch,
            'sns': mock_sns,
            'ses': mock_ses,
            's3': mock_s3,
            'api_gateway': mock_api_gateway
        }

@pytest.fixture
def mock_dynamodb_client(mock_aws_services):
    """Provide a mock DynamoDB client"""
    return mock_aws_services['dynamodb']

@pytest.fixture
def mock_cognito_client(mock_aws_services):
    """Provide a mock Cognito client"""
    return mock_aws_services['cognito']

@pytest.fixture
def mock_cloudwatch_client(mock_aws_services):
    """Provide a mock CloudWatch client"""
    return mock_aws_services['cloudwatch']
