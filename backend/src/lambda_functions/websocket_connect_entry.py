"""
WebSocket Connect Handler - Entry Point
🏆 Breaking Barriers UK 2026 compliant
Standalone handler with NO relative imports
"""

import json
import boto3
from datetime import datetime

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    """
    WebSocket $connect route handler
    Accepts connections and stores them in DynamoDB
    """
    try:
        connection_id = event['requestContext']['connectionId']
        domain_name = event['requestContext']['domainName']
        stage = event['requestContext']['stage']
        
        print(f"✅ WebSocket CONNECTED: {connection_id}")
        print(f"Domain: {domain_name}, Stage: {stage}")
        
        # Store connection in DynamoDB
        connections_table = dynamodb.Table('ai-therapy-platform-dev-websocket-connections')
        
        connections_table.put_item(
            Item={
                'connectionId': connection_id,
                'connectedAt': datetime.utcnow().isoformat(),
                'ttl': int((datetime.utcnow().timestamp() + 7200))  # 2 hours TTL
            }
        )
        
        print(f"✅ Connection stored in DynamoDB")
        
        # Send welcome message immediately after connection
        try:
            apigateway = boto3.client(
                'apigatewaymanagementapi',
                endpoint_url=f'https://{domain_name}/{stage}'
            )
            
            welcome_message = {
                'type': 'text',
                'payload': {
                    'text': 'Hello! I am Ally, your AI therapy companion. How are you feeling today?',
                    'isFromAI': True
                },
                'timestamp': datetime.utcnow().isoformat()
            }
            
            apigateway.post_to_connection(
                ConnectionId=connection_id,
                Data=json.dumps(welcome_message)
            )
            
            print(f"✅ Welcome message sent to {connection_id}")
            
        except Exception as e:
            print(f"⚠️ Failed to send welcome message: {str(e)}")
        
        # Return success
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Connected to Ally AI Therapy',
                'connectionId': connection_id
            })
        }
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
