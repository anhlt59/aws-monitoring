from __future__ import annotations

from src.adapters.db.mappers import LogAnalysisMapper
from src.adapters.db.models import LogAnalysisPersistence
from src.adapters.db.repositories.base import DynamoRepository
from src.common.exceptions import NotFoundError
from src.common.utils.encoding import base64_to_json
from src.domain.models import ListLogAnalysesDTO, LogAnalysis, LogAnalysisQueryResult


class LogAnalysisRepository(DynamoRepository):
    model_cls = LogAnalysisPersistence
    mapper = LogAnalysisMapper

    def get(self, analysis_id: str) -> LogAnalysis:
        """Get a log analysis by its ID (format: {date}#{hash})"""
        model = self._get(hash_key="LOG_ANALYSIS", range_key=analysis_id)
        return self.mapper.to_model(model)

    def get_by_date_and_hash(self, date: str, analysis_hash: str) -> LogAnalysis | None:
        """
        Get a log analysis by date and hash.
        Returns None if not found (used for deduplication).
        """
        try:
            persistence_id = f"LOG_ANALYSIS#{date}#{analysis_hash}"
            model = self._get(hash_key="LOG_ANALYSIS", range_key=persistence_id)
            return self.mapper.to_model(model)
        except NotFoundError:
            return None

    def list(self, dto: ListLogAnalysesDTO | None = None) -> LogAnalysisQueryResult:
        """List log analyses with optional filtering"""
        if dto is None:
            dto = ListLogAnalysesDTO()

        # Build range key condition for filtering by date
        range_key_condition = None
        if dto.date:
            # Exact date match: LOG_ANALYSIS#{date}#
            range_key_condition = self.model_cls.sk.begins_with(f"LOG_ANALYSIS#{dto.date}#")
        elif dto.start_date and dto.end_date:
            # Date range: LOG_ANALYSIS#{start_date} to LOG_ANALYSIS#{end_date}
            range_key_condition = self.model_cls.sk.between(
                f"LOG_ANALYSIS#{dto.start_date}#", f"LOG_ANALYSIS#{dto.end_date}#~"
            )
        elif dto.start_date:
            range_key_condition = self.model_cls.sk >= f"LOG_ANALYSIS#{dto.start_date}#"
        elif dto.end_date:
            range_key_condition = self.model_cls.sk <= f"LOG_ANALYSIS#{dto.end_date}#~"

        # Build filter condition for additional filters
        filter_condition = None
        if dto.account:
            filter_condition = self.model_cls.account == dto.account
        if dto.severity_min is not None:
            severity_filter = self.model_cls.severity >= dto.severity_min
            filter_condition = severity_filter if filter_condition is None else filter_condition & severity_filter

        last_evaluated_key = base64_to_json(dto.cursor) if dto.cursor else None
        scan_index_forward = "asc" == dto.direction

        result = self._query(
            hash_key="LOG_ANALYSIS",
            range_key_condition=range_key_condition,
            filter_condition=filter_condition,
            last_evaluated_key=last_evaluated_key,
            scan_index_forward=scan_index_forward,
            limit=dto.limit,
        )

        return LogAnalysisQueryResult(
            items=[self.mapper.to_model(item) for item in result],
            limit=dto.limit,
            cursor=result.last_evaluated_key,
        )

    def create(self, entity: LogAnalysis):
        """Create a new log analysis"""
        model = self.mapper.to_persistence(entity)
        self._create(model)

    def increment_frequency(self, date: str, analysis_hash: str, event_ids: list[str] | None = None):
        """
        Increment the frequency count for an existing analysis.
        Optionally add new event IDs.
        """
        persistence_id = f"LOG_ANALYSIS#{date}#{analysis_hash}"

        # Get current analysis to update event_ids
        current = self.get(persistence_id)

        # Merge event IDs
        updated_event_ids = list(set(current.event_ids + (event_ids or [])))

        self._update(
            hash_key="LOG_ANALYSIS",
            range_key=persistence_id,
            attributes={
                "frequency": current.frequency + 1,
                "event_ids": updated_event_ids,
                "updated_at": current.updated_at,
            },
        )

    def delete(self, analysis_id: str):
        """Delete a log analysis"""
        self._delete(hash_key="LOG_ANALYSIS", range_key=analysis_id)
