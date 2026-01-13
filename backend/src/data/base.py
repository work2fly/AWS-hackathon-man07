"""
Base repository class for DynamoDB operations
🏆 Breaking Barriers UK 2026 compliant
"""

import os
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
import boto3
from botocore.exceptions import ClientError, BotoCoreError
from ..config.aws_config import aws_clients
from ..utils.logger import get_logger

logger = get_logger(__name__)


class DynamoDBError(Exception):
    """Custom exception for DynamoDB operations"""
    pass


class BaseRepository(ABC):
    """Base repository class for DynamoDB operations"""
    
    def __init__(self, table_name: str):
        """Initialize repository with table name"""
        self.table_name = self._get_table_name(table_name)
        self.dynamodb_client = aws_clients.dynamodb
        self.dynamodb_resource = aws_clients.dynamodb_resource
        self.table = self.dynamodb_resource.Table(self.table_name)
        
    def _get_table_name(self, base_name: str) -> str:
        """Get full table name with environment prefix"""
        environment = os.getenv('ENVIRONMENT', 'dev')
        project_name = os.getenv('PROJECT_NAME', 'ai-therapy-platform')
        return f"{project_name}-{environment}-{base_name}"
    
    def _handle_dynamodb_error(self, error: Exception, operation: str) -> None:
        """Handle DynamoDB errors with proper logging"""
        if isinstance(error, ClientError):
            error_code = error.response['Error']['Code']
            error_message = error.response['Error']['Message']
            logger.error(f"DynamoDB {operation} failed: {error_code} - {error_message}")
            
            if error_code == 'ResourceNotFoundException':
                raise DynamoDBError(f"Table {self.table_name} not found")
            elif error_code == 'ValidationException':
                raise DynamoDBError(f"Invalid request: {error_message}")
            elif error_code == 'ConditionalCheckFailedException':
                raise DynamoDBError(f"Conditional check failed: {error_message}")
            elif error_code == 'ProvisionedThroughputExceededException':
                raise DynamoDBError(f"Throughput exceeded: {error_message}")
            else:
                raise DynamoDBError(f"DynamoDB error: {error_message}")
        else:
            logger.error(f"Unexpected error in {operation}: {str(error)}")
            raise DynamoDBError(f"Unexpected error: {str(error)}")
    
    def put_item(self, item: Dict[str, Any], condition_expression: Optional[str] = None) -> bool:
        """Put item into DynamoDB table"""
        try:
            put_kwargs = {'Item': item}
            if condition_expression:
                put_kwargs['ConditionExpression'] = condition_expression
                
            self.table.put_item(**put_kwargs)
            logger.info(f"Successfully put item in {self.table_name}")
            return True
            
        except Exception as e:
            self._handle_dynamodb_error(e, "put_item")
            return False
    
    def get_item(self, key: Dict[str, Any], consistent_read: bool = False) -> Optional[Dict[str, Any]]:
        """Get item from DynamoDB table"""
        try:
            response = self.table.get_item(
                Key=key,
                ConsistentRead=consistent_read
            )
            
            item = response.get('Item')
            if item:
                logger.info(f"Successfully retrieved item from {self.table_name}")
            else:
                logger.info(f"Item not found in {self.table_name}")
            
            return item
            
        except Exception as e:
            self._handle_dynamodb_error(e, "get_item")
            return None
    
    def update_item(self, key: Dict[str, Any], update_expression: str, 
                   expression_attribute_values: Dict[str, Any],
                   expression_attribute_names: Optional[Dict[str, str]] = None,
                   condition_expression: Optional[str] = None) -> bool:
        """Update item in DynamoDB table"""
        try:
            update_kwargs = {
                'Key': key,
                'UpdateExpression': update_expression,
                'ExpressionAttributeValues': expression_attribute_values,
                'ReturnValues': 'UPDATED_NEW'
            }
            
            if expression_attribute_names:
                update_kwargs['ExpressionAttributeNames'] = expression_attribute_names
            
            if condition_expression:
                update_kwargs['ConditionExpression'] = condition_expression
            
            self.table.update_item(**update_kwargs)
            logger.info(f"Successfully updated item in {self.table_name}")
            return True
            
        except Exception as e:
            self._handle_dynamodb_error(e, "update_item")
            return False
    
    def delete_item(self, key: Dict[str, Any], condition_expression: Optional[str] = None) -> bool:
        """Delete item from DynamoDB table"""
        try:
            delete_kwargs = {'Key': key}
            if condition_expression:
                delete_kwargs['ConditionExpression'] = condition_expression
            
            self.table.delete_item(**delete_kwargs)
            logger.info(f"Successfully deleted item from {self.table_name}")
            return True
            
        except Exception as e:
            self._handle_dynamodb_error(e, "delete_item")
            return False
    
    def query(self, key_condition_expression: str,
              expression_attribute_values: Dict[str, Any],
              expression_attribute_names: Optional[Dict[str, str]] = None,
              filter_expression: Optional[str] = None,
              index_name: Optional[str] = None,
              limit: Optional[int] = None,
              scan_index_forward: bool = True,
              exclusive_start_key: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Query items from DynamoDB table"""
        try:
            query_kwargs = {
                'KeyConditionExpression': key_condition_expression,
                'ExpressionAttributeValues': expression_attribute_values,
                'ScanIndexForward': scan_index_forward
            }
            
            if expression_attribute_names:
                query_kwargs['ExpressionAttributeNames'] = expression_attribute_names
            
            if filter_expression:
                query_kwargs['FilterExpression'] = filter_expression
            
            if index_name:
                query_kwargs['IndexName'] = index_name
            
            if limit:
                query_kwargs['Limit'] = limit
            
            if exclusive_start_key:
                query_kwargs['ExclusiveStartKey'] = exclusive_start_key
            
            response = self.table.query(**query_kwargs)
            logger.info(f"Successfully queried {len(response['Items'])} items from {self.table_name}")
            
            return response
            
        except Exception as e:
            self._handle_dynamodb_error(e, "query")
            return {'Items': [], 'Count': 0}
    
    def scan(self, filter_expression: Optional[str] = None,
             expression_attribute_values: Optional[Dict[str, Any]] = None,
             expression_attribute_names: Optional[Dict[str, str]] = None,
             limit: Optional[int] = None,
             exclusive_start_key: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Scan items from DynamoDB table"""
        try:
            scan_kwargs = {}
            
            if filter_expression:
                scan_kwargs['FilterExpression'] = filter_expression
            
            if expression_attribute_values:
                scan_kwargs['ExpressionAttributeValues'] = expression_attribute_values
            
            if expression_attribute_names:
                scan_kwargs['ExpressionAttributeNames'] = expression_attribute_names
            
            if limit:
                scan_kwargs['Limit'] = limit
            
            if exclusive_start_key:
                scan_kwargs['ExclusiveStartKey'] = exclusive_start_key
            
            response = self.table.scan(**scan_kwargs)
            logger.info(f"Successfully scanned {len(response['Items'])} items from {self.table_name}")
            
            return response
            
        except Exception as e:
            self._handle_dynamodb_error(e, "scan")
            return {'Items': [], 'Count': 0}
    
    def batch_get_items(self, keys: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Batch get items from DynamoDB table"""
        try:
            if not keys:
                return []
            
            # DynamoDB batch_get_item has a limit of 100 items
            batch_size = 100
            all_items = []
            
            for i in range(0, len(keys), batch_size):
                batch_keys = keys[i:i + batch_size]
                
                response = self.dynamodb_resource.batch_get_item(
                    RequestItems={
                        self.table_name: {
                            'Keys': batch_keys
                        }
                    }
                )
                
                items = response.get('Responses', {}).get(self.table_name, [])
                all_items.extend(items)
                
                # Handle unprocessed keys
                unprocessed_keys = response.get('UnprocessedKeys', {})
                while unprocessed_keys:
                    response = self.dynamodb_resource.batch_get_item(
                        RequestItems=unprocessed_keys
                    )
                    items = response.get('Responses', {}).get(self.table_name, [])
                    all_items.extend(items)
                    unprocessed_keys = response.get('UnprocessedKeys', {})
            
            logger.info(f"Successfully batch retrieved {len(all_items)} items from {self.table_name}")
            return all_items
            
        except Exception as e:
            self._handle_dynamodb_error(e, "batch_get_items")
            return []
    
    def batch_write_items(self, items: List[Dict[str, Any]], delete_keys: Optional[List[Dict[str, Any]]] = None) -> bool:
        """Batch write items to DynamoDB table"""
        try:
            if not items and not delete_keys:
                return True
            
            # DynamoDB batch_write_item has a limit of 25 items
            batch_size = 25
            
            # Process put requests
            if items:
                for i in range(0, len(items), batch_size):
                    batch_items = items[i:i + batch_size]
                    
                    request_items = {
                        self.table_name: [
                            {'PutRequest': {'Item': item}} for item in batch_items
                        ]
                    }
                    
                    response = self.dynamodb_resource.batch_write_item(
                        RequestItems=request_items
                    )
                    
                    # Handle unprocessed items
                    unprocessed_items = response.get('UnprocessedItems', {})
                    while unprocessed_items:
                        response = self.dynamodb_resource.batch_write_item(
                            RequestItems=unprocessed_items
                        )
                        unprocessed_items = response.get('UnprocessedItems', {})
            
            # Process delete requests
            if delete_keys:
                for i in range(0, len(delete_keys), batch_size):
                    batch_keys = delete_keys[i:i + batch_size]
                    
                    request_items = {
                        self.table_name: [
                            {'DeleteRequest': {'Key': key}} for key in batch_keys
                        ]
                    }
                    
                    response = self.dynamodb_resource.batch_write_item(
                        RequestItems=request_items
                    )
                    
                    # Handle unprocessed items
                    unprocessed_items = response.get('UnprocessedItems', {})
                    while unprocessed_items:
                        response = self.dynamodb_resource.batch_write_item(
                            RequestItems=unprocessed_items
                        )
                        unprocessed_items = response.get('UnprocessedItems', {})
            
            logger.info(f"Successfully batch wrote items to {self.table_name}")
            return True
            
        except Exception as e:
            self._handle_dynamodb_error(e, "batch_write_items")
            return False