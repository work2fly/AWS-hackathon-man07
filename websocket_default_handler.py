"""
WebSocket Default Handler - Lambda Entry Point
🏆 Breaking Barriers UK 2026 compliant
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from lambda_functions.websocket_handlers import default_handler

def lambda_handler(event, context):
    """Lambda entry point for WebSocket default route"""
    return default_handler(event, context)
