from datetime import datetime
from typing import List, Optional

import boto3
from botocore.exceptions import ClientError

from src.common.logger import logger
from src.domain.agent.entities.log_entry import LogEntry
from src.domain.agent.ports.log_reader import LogReader




class CloudWatchLogReader(LogReader):
    """CloudWatch implementation of LogReader port"""

    def __init__(self):
        self.client = boto3.client("logs")

    async def read_logs(
        self,
        log_group: str,
        start_time: datetime,
        end_time: datetime,
        filter_pattern: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[LogEntry]:
        """Read logs from CloudWatch log group"""
        try:
            # Convert datetime to milliseconds
            start_time_ms = int(start_time.timestamp() * 1000)
            end_time_ms = int(end_time.timestamp() * 1000)

            # Prepare filter logs parameters
            params = {
                "logGroupName": log_group,
                "startTime": start_time_ms,
                "endTime": end_time_ms,
            }

            if filter_pattern:
                params["filterPattern"] = filter_pattern

            if limit:
                params["limit"] = limit

            # Filter logs
            response = self.client.filter_log_events(**params)

            log_entries = []
            for event in response.get("events", []):
                try:
                    log_entry = LogEntry.from_cloudwatch_log(
                        timestamp=datetime.fromtimestamp(event["timestamp"] / 1000),
                        message=event["message"],
                        log_group=log_group,
                        log_stream=event["logStreamName"],
                        metadata={
                            "event_id": event.get("eventId"),
                            "ingestion_time": event.get("ingestionTime"),
                        },
                    )
                    log_entries.append(log_entry)

                except Exception as e:
                    logger.warning(f"Failed to parse log event: {e}")
                    continue

            logger.debug(f"Read {len(log_entries)} logs from {log_group}")
            return log_entries

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "ResourceNotFoundException":
                logger.warning(f"Log group not found: {log_group}")
                return []
            else:
                logger.error(f"CloudWatch error reading logs from {log_group}: {e}")
                raise

        except Exception as e:
            logger.error(f"Failed to read logs from {log_group}: {e}")
            raise

    async def read_error_logs(
        self,
        log_group: str,
        start_time: datetime,
        end_time: datetime,
        limit: Optional[int] = None,
    ) -> List[LogEntry]:
        """Read only error-level logs from CloudWatch"""
        # Use filter pattern to find error logs
        error_patterns = [
            "ERROR",
            "CRITICAL",
            "FATAL",
            "Exception",
            "error",
            "failed",
            "failure",
        ]

        # Create filter pattern for errors
        filter_pattern = " OR ".join(f'"{pattern}"' for pattern in error_patterns)

        return await self.read_logs(
            log_group=log_group,
            start_time=start_time,
            end_time=end_time,
            filter_pattern=filter_pattern,
            limit=limit,
        )

    async def search_logs(
        self,
        log_groups: List[str],
        query: str,
        start_time: datetime,
        end_time: datetime,
        limit: Optional[int] = None,
    ) -> List[LogEntry]:
        """Search logs across multiple log groups using CloudWatch Insights"""
        try:
            # Convert datetime to epoch seconds
            start_time_epoch = int(start_time.timestamp())
            end_time_epoch = int(end_time.timestamp())

            # Build CloudWatch Insights query
            insights_query = f"""
            fields @timestamp, @message, @logStream
            | filter @message like /{query}/
            | sort @timestamp desc
            """

            if limit:
                insights_query += f"\n| limit {limit}"

            # Start query
            response = self.client.start_query(
                logGroupNames=log_groups,
                startTime=start_time_epoch,
                endTime=end_time_epoch,
                queryString=insights_query,
            )

            query_id = response["queryId"]

            # Poll for results
            import time

            max_attempts = 30  # 30 seconds timeout
            for attempt in range(max_attempts):
                result_response = self.client.get_query_results(queryId=query_id)

                if result_response["status"] == "Complete":
                    break
                elif result_response["status"] == "Failed":
                    raise Exception(f"CloudWatch Insights query failed: {result_response}")

                time.sleep(1)  # Wait 1 second between polls

            else:
                raise Exception("CloudWatch Insights query timeout")

            # Parse results
            log_entries = []
            for result in result_response.get("results", []):
                try:
                    # Extract fields from result
                    fields = {item["field"]: item["value"] for item in result}

                    # Determine log group (may not be directly available in results)
                    log_group = log_groups[0] if len(log_groups) == 1 else "multiple"

                    log_entry = LogEntry.from_cloudwatch_log(
                        timestamp=datetime.fromisoformat(fields["@timestamp"].replace("Z", "+00:00")),
                        message=fields["@message"],
                        log_group=log_group,
                        log_stream=fields["@logStream"],
                        metadata={"query": query, "insights_result": True},
                    )
                    log_entries.append(log_entry)

                except Exception as e:
                    logger.warning(f"Failed to parse Insights result: {e}")
                    continue

            logger.debug(f"Found {len(log_entries)} logs via Insights query")
            return log_entries

        except Exception as e:
            logger.error(f"Failed to search logs with Insights: {e}")
            # Fallback to regular filter for single log group
            if len(log_groups) == 1:
                logger.info("Falling back to filter_log_events")
                return await self.read_logs(
                    log_group=log_groups[0],
                    start_time=start_time,
                    end_time=end_time,
                    filter_pattern=query,
                    limit=limit,
                )
            raise
