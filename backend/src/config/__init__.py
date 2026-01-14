"""
Configuration module for AI Therapy Platform
"""

from .aws_config import aws_clients, AWS_REGION, get_account_id
from .nova_sonic_config import NovaSonicConfig, NovaSonicClient, nova_sonic_client

__all__ = [
    'aws_clients',
    'AWS_REGION',
    'get_account_id',
    'NovaSonicConfig',
    'NovaSonicClient',
    'nova_sonic_client'
]