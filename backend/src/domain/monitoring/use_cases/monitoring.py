from typing import Iterable
from datetime import datetime, timedelta, UTC

from src.adapters.db.repositories import EventRepository
from src.adapters.logs import LogService
from src.adapters.publisher import Publisher
from src.common.exceptions import NotFoundError, ConflictError
from src.common.utils.objects import chunks

from ..models import Event, LogQuery, LogQueryResult, Message
from ..dtos import ListEventsDTO, PaginatedEventsDTO
from ..exceptions import EventNotFoundError, EventConflictError


class MonitoringUseCases:
    def __init__(self, log_service: LogService, publisher: Publisher):
        self.publisher = publisher
        self.log_service = log_service

    def query_error_logs(self, query: LogQuery) ->:
        # list monitoring log groups
        log_groups = self.log_service.list_monitoring_log_groups_by_tag(query.filter_tag["key"],
                                                                        query.filter_tag["value"])

        for chunk in chunks(log_groups, query.chunk_size):
            # query error logs from CloudWatch Logs
            yield from self.log_service.query_logs(
                chunk,
                query_string=query.query_string,
                start_time=query.start_time,
                end_time=query.end_time,
                timeout=query.timeout,
                delay=query.delay,
            )

    def run_query_and_publish_error_logs(self, query: LogQuery):
        # list monitoring log groups
        log_groups = self.log_service.list_monitoring_log_groups_by_tag(query.filter_tag["key"],
                                                                        query.filter_tag["value"])

        for chunk in chunks(log_groups, query.chunk_size):
            # query error logs from CloudWatch Logs
            error_logs = self.log_service.query_logs(
                chunk,
                query_string=query.query_string,
                start_time=query.start_time,
                end_time=query.end_time,
                timeout=query.timeout,
                delay=query.delay,
            )

            # publish the results to the message broker
            if messages := [
                Message(
                    source="monitoring.agent.logs",
                    detail_type="Error Log Query",
                    detail=log_result.model_dump_json(),
                    resources=[log_result.log_group_name],
                )
                for log_result in error_logs
            ]:
                self.publisher.publish(messages)
