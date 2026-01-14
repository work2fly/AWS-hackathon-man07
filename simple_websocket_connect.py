"""
Simple WebSocket Connect Handler - Quick Fix
🏆 Breaking Barriers UK 2026 compliant
"""

import json
from datetime import datetime

def lambda_handler(event, context):
    """
    Simple WebSocket connect handler that accepts all connections
    """
    connection_id = event['requestContext']['connectionId']
    
    print(f"✅ WebSocket connection: {connection_id}")
    print(f"Event: {json.dumps(event)}")
    
    # Accept the connection
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Connected'})
    }
