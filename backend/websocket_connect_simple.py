"""
Simple WebSocket Connect Handler - Demo Mode
🏆 Breaking Barriers UK 2026 compliant
"""

import json
import boto3
import os
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
connections_table = dynamodb.Table(os.environ['CONNECTIONS_TABLE_NAME'])

def handler(event, context):
    """Handle WebSocket $connect route - simplified for demo"""
    try:
        connection_id = event['requestContext']['connectionId']
        domain_name = event['requestContext']['domainName']
        stage = event['requestContext']['stage']
        
        print(f"✅ WebSocket CONNECTED: {connection_id}")
        print(f"Domain: {domain_name}, Stage: {stage}")
        
        # Demo mode - create demo user
        user_id = f'demo_user_{int(datetime.utcnow().timestamp())}'
        
        # Store connection in DynamoDB
        connections_table.put_item(
            Item={
                'connectionId': connection_id,
                'userId': user_id,
                'connectedAt': datetime.utcnow().isoformat(),
                'ttl': int(datetime.utcnow().timestamp()) + 7200  # 2 hours
            }
        )
        
        print(f"✅ Connection stored in DynamoDB")
        
        # Send welcome message
        try:
            apigateway = boto3.client('apigatewaymanagementapi',
                endpoint_url=f'https://{domain_name}/{stage}')
            
            welcome_message = {
                'type': 'connection_established',
                'message': 'Connected to AI Therapy Platform',
                'user_id': user_id,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            apigateway.post_to_connection(
                ConnectionId=connection_id,
                Data=json.dumps(welcome_message)
            )
            print(f"✅ Welcome message sent")
        except Exception as e:
            print(f"⚠️ Failed to send welcome message: {str(e)}")
        
        return {'statusCode': 200}
        
    except Exception as e:
        print(f"❌ Connect handler error: {str(e)}")
        return {'statusCode': 500, 'body': json.dumps({'error': 'Internal server error'})}
