from src.adapters.db.models import LogAnalysisPersistence
from src.domain.models import LogAnalysis


class LogAnalysisMapper:
    @classmethod
    def to_persistence(cls, model: LogAnalysis) -> LogAnalysisPersistence:
        return LogAnalysisPersistence(
            # Keys
            pk="LOG_ANALYSIS",
            sk=model.persistence_id,
            # Attributes
            date=model.date,
            analysis_hash=model.id,
            context_ids=model.context_ids,
            severity=model.severity,
            categories=model.categories,
            patterns=model.patterns,
            frequency=model.frequency,
            summary=model.summary,
            solution=model.solution,
            log_sample=model.log_sample,
            event_ids=model.event_ids,
            account=model.account,
            region=model.region,
            analyzed_at=model.analyzed_at,
            updated_at=model.updated_at,
        )

    @classmethod
    def to_model(cls, persistence: LogAnalysisPersistence) -> LogAnalysis:
        return LogAnalysis(
            id=persistence.analysis_hash,
            date=persistence.date,
            context_ids=persistence.context_ids or [],
            severity=persistence.severity,
            categories=persistence.categories or [],
            patterns=persistence.patterns or [],
            frequency=persistence.frequency,
            summary=persistence.summary,
            solution=persistence.solution,
            log_sample=persistence.log_sample,
            event_ids=persistence.event_ids or [],
            account=persistence.account,
            region=persistence.region,
            analyzed_at=persistence.analyzed_at,
            updated_at=persistence.updated_at,
        )
