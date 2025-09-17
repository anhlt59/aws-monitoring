from typing import List

from src.common.logger import Logger
from src.domain.agent.dtos.log_dtos import LogQueryDTO, LogSummaryDTO
from src.domain.agent.entities.log_entry import LogEntry
from src.domain.agent.ports.event_publisher import EventPublisher
from src.domain.agent.ports.log_reader import LogReader
from src.domain.agent.value_objects.log_level import LogLevel

logger = Logger(__name__)


class QueryErrorLogsUseCase:
    """Use case for querying and processing error logs"""

    def __init__(self, log_reader: LogReader, event_publisher: EventPublisher):
        self.log_reader = log_reader
        self.event_publisher = event_publisher

    async def execute(self, query_dto: LogQueryDTO, account: str, region: str) -> LogSummaryDTO:
        """Query logs and publish error events"""
        try:
            # Read logs from CloudWatch
            log_entries = await self._query_logs(query_dto)
            logger.info(f"Found {len(log_entries)} log entries")

            # Filter and process error logs
            error_logs = self._filter_error_logs(log_entries, query_dto.log_level)

            # Publish error events to master
            if error_logs:
                await self._publish_error_events(error_logs, account, region)

            # Generate summary
            summary = self._generate_summary(log_entries, query_dto)

            return summary

        except Exception as e:
            logger.error(f"Failed to query error logs: {e}")
            raise

    async def _query_logs(self, query_dto: LogQueryDTO) -> List[LogEntry]:
        """Query logs from multiple log groups"""
        all_logs = []

        for log_group in query_dto.log_groups:
            try:
                if query_dto.filter_pattern:
                    # Use filter pattern if provided
                    logs = await self.log_reader.read_logs(
                        log_group=log_group,
                        start_time=query_dto.start_time,
                        end_time=query_dto.end_time,
                        filter_pattern=query_dto.filter_pattern,
                        limit=query_dto.limit,
                    )
                else:
                    # Read all logs if no filter
                    logs = await self.log_reader.read_logs(
                        log_group=log_group,
                        start_time=query_dto.start_time,
                        end_time=query_dto.end_time,
                        limit=query_dto.limit,
                    )

                all_logs.extend(logs)
                logger.debug(f"Found {len(logs)} logs in {log_group}")

            except Exception as e:
                logger.warning(f"Failed to read logs from {log_group}: {e}")
                continue

        return all_logs

    def _filter_error_logs(self, log_entries: List[LogEntry], min_level: LogLevel = None) -> List[LogEntry]:
        """Filter logs by minimum severity level"""
        if not min_level:
            min_level = LogLevel.ERROR

        min_weight = min_level.get_severity_weight()
        return [log for log in log_entries if log.level.get_severity_weight() >= min_weight]

    async def _publish_error_events(self, error_logs: List[LogEntry], account: str, region: str) -> None:
        """Publish error logs as monitoring events"""
        logger.info(f"Publishing {len(error_logs)} error events")

        # Batch publish for efficiency
        if len(error_logs) > 10:
            # Publish in batches
            await self.event_publisher.publish_batch_log_events(
                log_entries=error_logs, additional_metadata={"account": account, "region": region}
            )
        else:
            # Publish individually for small sets
            for log in error_logs:
                await self.event_publisher.publish_log_event(
                    log_entry=log, additional_metadata={"account": account, "region": region}
                )

    def _generate_summary(self, log_entries: List[LogEntry], query_dto: LogQueryDTO) -> LogSummaryDTO:
        """Generate summary statistics for logs"""
        level_counts = {
            LogLevel.DEBUG: 0,
            LogLevel.INFO: 0,
            LogLevel.WARNING: 0,
            LogLevel.ERROR: 0,
            LogLevel.CRITICAL: 0,
        }

        for log in log_entries:
            level_counts[log.level] += 1

        return LogSummaryDTO(
            total_logs=len(log_entries),
            error_count=level_counts[LogLevel.ERROR] + level_counts[LogLevel.CRITICAL],
            warning_count=level_counts[LogLevel.WARNING],
            info_count=level_counts[LogLevel.INFO],
            debug_count=level_counts[LogLevel.DEBUG],
            time_range={
                "start": query_dto.start_time.isoformat(),
                "end": query_dto.end_time.isoformat(),
            },
            log_groups=query_dto.log_groups,
        )
