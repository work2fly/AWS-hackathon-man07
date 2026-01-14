"""
WebSocket Connect Handler - Lambda Entry Point
🏆 Breaking Barriers UK 2026 compliant
"""

import json
from datetime import datetime

def lambda_handler(event, context):
    """
    Simple WebSocket connect handler
    Accepts all connections and logs the event
    """
    try:
        connection_id = event['requestContext']['connectionId']
        
        print(f"✅ WebSocket connection: {connection_id}")
        print(f"Event: {json.dumps(event, default=str)}")
        
        # TODO: Add authentication and user lookup
        # For now, accept all connections
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Connected', 'connectionId': connection_id})
        }
    except Exception as e:
        print(f"❌ Error in connect handler: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
