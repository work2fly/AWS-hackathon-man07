"""
AI Therapy Platform - CloudWatch Metrics Utility
Breaking Barriers UK 2026 compliant metrics and monitoring
"""

import boto3
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from contextlib import contextmanager
from ..config.aws_config import aws_clients
from .logger import logger

class MetricsCollector:
    """
    Centralized metrics collection for CloudWatch
    Handles custom metrics, performance tracking, and business metrics
    """
    
    def __init__(self):
        self.cloudwatch = aws_clients.cloudwatch
        self.namespace = "AI-Therapy-Platform"
        self.default_dimensions = {
            'Environment': 'dev',  # Will be set from environment variable
            'Service': 'backend'
        }
    
    def put_metric(self, metric_name: str, value: float, unit: str = 'Count',
                   dimensions: Optional[Dict[str, str]] = None, 
                   timestamp: Optional[datetime] = None):
        """
        Put a single metric to CloudWatch
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            unit: CloudWatch unit (Count, Seconds, Bytes, etc.)
            dimensions: Additional dimensions for the metric
            timestamp: Metric timestamp (defaults to now)
        """
        try:
            metric_dimensions = self.default_dimensions.copy()
            if dimensions:
                metric_dimensions.update(dimensions)
            
            # Convert dimensions to CloudWatch format
            cw_dimensions = [
                {'Name': key, 'Value': value} 
                for key, value in metric_dimensions.items()
            ]
            
            self.cloudwatch.put_metric_data(
                Namespace=self.namespace,
                MetricData=[
                    {
                        'MetricName': metric_name,
                        'Value': value,
                        'Unit': unit,
                        'Dimensions': cw_dimensions,
                        'Timestamp': timestamp or datetime.utcnow()
                    }
                ]
            )
            
            logger.debug(
                f"Metric sent to CloudWatch: {metric_name}",
                metric_name=metric_name,
                value=value,
                unit=unit,
                dimensions=metric_dimensions
            )
            
        except Exception as e:
            logger.error(
                f"Failed to send metric to CloudWatch: {metric_name}",
                error=e,
                metric_name=metric_name,
                value=value
            )
    
    def put_metrics_batch(self, metrics: List[Dict[str, Any]]):
        """
        Put multiple metrics to CloudWatch in a single request
        
        Args:
            metrics: List of metric dictionaries with keys:
                    - name: metric name
                    - value: metric value
                    - unit: CloudWatch unit (optional, defaults to 'Count')
                    - dimensions: additional dimensions (optional)
                    - timestamp: metric timestamp (optional)
        """
        try:
            metric_data = []
            
            for metric in metrics:
                metric_dimensions = self.default_dimensions.copy()
                if metric.get('dimensions'):
                    metric_dimensions.update(metric['dimensions'])
                
                cw_dimensions = [
                    {'Name': key, 'Value': value} 
                    for key, value in metric_dimensions.items()
                ]
                
                metric_data.append({
                    'MetricName': metric['name'],
                    'Value': metric['value'],
                    'Unit': metric.get('unit', 'Count'),
                    'Dimensions': cw_dimensions,
                    'Timestamp': metric.get('timestamp', datetime.utcnow())
                })
            
            # CloudWatch allows max 20 metrics per request
            for i in range(0, len(metric_data), 20):
                batch = metric_data[i:i+20]
                self.cloudwatch.put_metric_data(
                    Namespace=self.namespace,
                    MetricData=batch
                )
            
            logger.debug(
                f"Batch metrics sent to CloudWatch",
                metric_count=len(metrics)
            )
            
        except Exception as e:
            logger.error(
                f"Failed to send batch metrics to CloudWatch",
                error=e,
                metric_count=len(metrics)
            )
    
    # Business Metrics
    def record_session_started(self, user_id: str, session_type: str = 'therapy'):
        """Record when a therapy session starts"""
        self.put_metric(
            'SessionsStarted',
            1,
            dimensions={
                'UserId': user_id,
                'SessionType': session_type
            }
        )
    
    def record_session_completed(self, user_id: str, duration_seconds: float, 
                               session_type: str = 'therapy'):
        """Record when a therapy session completes"""
        self.put_metrics_batch([
            {
                'name': 'SessionsCompleted',
                'value': 1,
                'dimensions': {
                    'UserId': user_id,
                    'SessionType': session_type
                }
            },
            {
                'name': 'SessionDuration',
                'value': duration_seconds,
                'unit': 'Seconds',
                'dimensions': {
                    'UserId': user_id,
                    'SessionType': session_type
                }
            }
        ])
    
    def record_red_flag_detected(self, flag_type: str, severity: str, user_id: str):
        """Record red flag detection"""
        self.put_metric(
            'RedFlagsDetected',
            1,
            dimensions={
                'FlagType': flag_type,
                'Severity': severity,
                'UserId': user_id
            }
        )
    
    def record_user_registration(self, user_role: str):
        """Record user registration"""
        self.put_metric(
            'UserRegistrations',
            1,
            dimensions={
                'UserRole': user_role
            }
        )
    
    def record_authentication_attempt(self, success: bool, method: str = 'password'):
        """Record authentication attempt"""
        self.put_metric(
            'AuthenticationAttempts',
            1,
            dimensions={
                'Success': str(success),
                'Method': method
            }
        )
    
    # Performance Metrics
    def record_api_request(self, method: str, endpoint: str, status_code: int, 
                          duration_ms: float):
        """Record API request metrics"""
        self.put_metrics_batch([
            {
                'name': 'APIRequests',
                'value': 1,
                'dimensions': {
                    'Method': method,
                    'Endpoint': endpoint,
                    'StatusCode': str(status_code)
                }
            },
            {
                'name': 'APILatency',
                'value': duration_ms,
                'unit': 'Milliseconds',
                'dimensions': {
                    'Method': method,
                    'Endpoint': endpoint
                }
            }
        ])
    
    def record_database_operation(self, operation: str, table: str, 
                                success: bool, duration_ms: float):
        """Record database operation metrics"""
        self.put_metrics_batch([
            {
                'name': 'DatabaseOperations',
                'value': 1,
                'dimensions': {
                    'Operation': operation,
                    'Table': table,
                    'Success': str(success)
                }
            },
            {
                'name': 'DatabaseLatency',
                'value': duration_ms,
                'unit': 'Milliseconds',
                'dimensions': {
                    'Operation': operation,
                    'Table': table
                }
            }
        ])
    
    def record_bedrock_request(self, model_id: str, success: bool, 
                             duration_ms: float, tokens_used: Optional[int] = None):
        """Record Bedrock API request metrics"""
        metrics = [
            {
                'name': 'BedrockRequests',
                'value': 1,
                'dimensions': {
                    'ModelId': model_id,
                    'Success': str(success)
                }
            },
            {
                'name': 'BedrockLatency',
                'value': duration_ms,
                'unit': 'Milliseconds',
                'dimensions': {
                    'ModelId': model_id
                }
            }
        ]
        
        if tokens_used is not None:
            metrics.append({
                'name': 'BedrockTokensUsed',
                'value': tokens_used,
                'dimensions': {
                    'ModelId': model_id
                }
            })
        
        self.put_metrics_batch(metrics)
    
    def record_websocket_connection(self, action: str, success: bool):
        """Record WebSocket connection metrics"""
        self.put_metric(
            'WebSocketConnections',
            1,
            dimensions={
                'Action': action,  # connect, disconnect, message
                'Success': str(success)
            }
        )

# Global metrics collector instance
metrics = MetricsCollector()

# Context managers for automatic performance tracking
@contextmanager
def track_api_performance(method: str, endpoint: str):
    """Context manager to automatically track API performance"""
    start_time = time.time()
    status_code = 200
    
    try:
        yield
    except Exception as e:
        status_code = 500
        raise
    finally:
        duration_ms = (time.time() - start_time) * 1000
        metrics.record_api_request(method, endpoint, status_code, duration_ms)

@contextmanager
def track_database_performance(operation: str, table: str):
    """Context manager to automatically track database performance"""
    start_time = time.time()
    success = True
    
    try:
        yield
    except Exception as e:
        success = False
        raise
    finally:
        duration_ms = (time.time() - start_time) * 1000
        metrics.record_database_operation(operation, table, success, duration_ms)

@contextmanager
def track_bedrock_performance(model_id: str):
    """Context manager to automatically track Bedrock performance"""
    start_time = time.time()
    success = True
    
    try:
        yield
    except Exception as e:
        success = False
        raise
    finally:
        duration_ms = (time.time() - start_time) * 1000
        metrics.record_bedrock_request(model_id, success, duration_ms)

# Decorator for Lambda functions to automatically track performance
def track_lambda_performance(func):
    """Decorator to automatically track Lambda function performance"""
    def wrapper(event, context):
        start_time = time.time()
        success = True
        
        try:
            result = func(event, context)
            return result
        except Exception as e:
            success = False
            raise
        finally:
            duration_ms = (time.time() - start_time) * 1000
            metrics.put_metric(
                'LambdaExecutionTime',
                duration_ms,
                'Milliseconds',
                dimensions={
                    'FunctionName': context.function_name,
                    'Success': str(success)
                }
            )
    
    return wrapper