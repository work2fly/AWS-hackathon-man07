"""
Simple WebSocket Disconnect Handler - Demo Mode
🏆 Breaking Barriers UK 2026 compliant
"""

import json
import boto3
import os
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
connections_table = dynamodb.Table(os.environ['CONNECTIONS_TABLE_NAME'])

def handler(event, context):
    """Handle WebSocket $disconnect route - simplified for demo"""
    try:
        connection_id = event['requestContext']['connectionId']
        
        print(f"🔴 WebSocket DISCONNECTED: {connection_id}")
        
        # Remove connection from DynamoDB
        connections_table.delete_item(Key={'connectionId': connection_id})
        
        print(f"✅ Connection removed from DynamoDB")
        
        return {'statusCode': 200}
        
    except Exception as e:
        print(f"❌ Disconnect handler error: {str(e)}")
        # Still return 200 to avoid errors
        return {'statusCode': 200}
