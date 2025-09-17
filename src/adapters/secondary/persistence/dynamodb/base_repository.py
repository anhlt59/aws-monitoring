import os
from typing import Any, Dict, List, Optional

import boto3
from botocore.exceptions import ClientError

from src.common.logger import logger




class BaseDynamoDBRepository:
    """Base class for DynamoDB repositories"""

    def __init__(self, table_name: Optional[str] = None):
        # Use provided table name or get from environment
        self.table_name = table_name or os.environ.get("DYNAMODB_TABLE_NAME", "monitoring-table")

        # Initialize DynamoDB resource
        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(self.table_name)

        logger.debug(f"Initialized DynamoDB repository for table: {self.table_name}")

    async def _put_item(self, item: Dict[str, Any]) -> None:
        """Put item into DynamoDB table"""
        try:
            self.table.put_item(Item=item)
            logger.debug(f"Item saved: {item.get('pk', 'unknown')}")
        except ClientError as e:
            logger.error(f"Failed to put item: {e}")
            raise

    async def _get_item(self, key: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get item from DynamoDB table"""
        try:
            response = self.table.get_item(Key=key)
            return response.get("Item")
        except ClientError as e:
            logger.error(f"Failed to get item: {e}")
            raise

    async def _query(
        self,
        key_condition_expression: str,
        expression_attribute_values: Dict[str, Any],
        index_name: Optional[str] = None,
        limit: Optional[int] = None,
        scan_index_forward: bool = True,
    ) -> List[Dict[str, Any]]:
        """Query items from DynamoDB table"""
        try:
            query_params = {
                "KeyConditionExpression": key_condition_expression,
                "ExpressionAttributeValues": expression_attribute_values,
                "ScanIndexForward": scan_index_forward,
            }

            if index_name:
                query_params["IndexName"] = index_name

            if limit:
                query_params["Limit"] = limit

            response = self.table.query(**query_params)
            return response.get("Items", [])

        except ClientError as e:
            logger.error(f"Failed to query items: {e}")
            raise

    async def _scan(
        self,
        filter_expression: Optional[str] = None,
        expression_attribute_values: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Scan items from DynamoDB table"""
        try:
            scan_params = {}

            if filter_expression:
                scan_params["FilterExpression"] = filter_expression

            if expression_attribute_values:
                scan_params["ExpressionAttributeValues"] = expression_attribute_values

            if limit:
                scan_params["Limit"] = limit

            response = self.table.scan(**scan_params)
            return response.get("Items", [])

        except ClientError as e:
            logger.error(f"Failed to scan items: {e}")
            raise

    async def _delete_item(self, key: Dict[str, Any]) -> bool:
        """Delete item from DynamoDB table"""
        try:
            self.table.delete_item(Key=key)
            logger.debug(f"Item deleted: {key}")
            return True
        except ClientError as e:
            logger.error(f"Failed to delete item: {e}")
            return False

    async def _batch_write(self, items: List[Dict[str, Any]]) -> None:
        """Batch write items to DynamoDB table"""
        try:
            with self.table.batch_writer() as batch:
                for item in items:
                    batch.put_item(Item=item)

            logger.debug(f"Batch write completed: {len(items)} items")

        except ClientError as e:
            logger.error(f"Failed to batch write items: {e}")
            raise
