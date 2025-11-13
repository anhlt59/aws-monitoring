"""
AI-powered log analysis use case.

Batch processes logs from recent events to:
1. Extract log messages from events
2. Deduplicate similar logs (>85% similarity)
3. Sanitize sensitive data
4. Analyze with AI
5. Store or update analysis results
6. Link events to analysis
"""

import hashlib
from datetime import datetime, timedelta

from pydantic import BaseModel

from src.adapters.db.repositories import ContextRepository, EventRepository, LogAnalysisRepository
from src.common.logger import logger
from src.common.utils.datetime_utils import current_utc_timestamp
from src.common.utils.sanitization import sanitize_logs
from src.common.utils.text_similarity import deduplicate_texts
from src.domain.models import CreateLogAnalysisDTO, Event, ListEventsDTO, LogAnalysis
from src.domain.ports.ai_analyzer import IAILogAnalyzer


class AILogAnalysisParams(BaseModel):
    """Parameters for AI log analysis"""

    lookback_minutes: int = 10  # How far back to query events
    similarity_threshold: float = 0.85  # Threshold for duplicate detection (85%)
    max_logs_per_batch: int = 100  # Maximum logs to analyze in one batch
    context_types: list[str] | None = None  # Context types to include (e.g., ["backend", "database"])


def ai_log_analysis_use_case(
    params: AILogAnalysisParams,
    event_repository: EventRepository,
    log_analysis_repository: LogAnalysisRepository,
    context_repository: ContextRepository,
    ai_analyzer: IAILogAnalyzer,
) -> list[LogAnalysis]:
    """
    AI-powered log analysis batch processing use case.

    Workflow:
    1. Query events from the last N minutes
    2. Extract and deduplicate log messages
    3. Sanitize sensitive data
    4. Load system context for AI understanding
    5. Analyze logs with AI
    6. Check for existing similar analysis (same day)
    7. Create new or update existing analysis
    8. Link events to analysis

    Args:
        params: Analysis parameters
        event_repository: Event repository
        log_analysis_repository: Log analysis repository
        context_repository: Context repository
        ai_analyzer: AI analyzer service

    Returns:
        List of created or updated log analyses
    """
    logger.info(f"Starting AI log analysis batch processing (lookback: {params.lookback_minutes}m)")

    # 1. Query recent events
    end_time = current_utc_timestamp()
    start_time = end_time - (params.lookback_minutes * 60)

    events_dto = ListEventsDTO(
        start_date=start_time,
        end_date=end_time,
        limit=1000,  # Large limit to get all recent events
    )

    events_result = event_repository.list(events_dto)
    events = events_result.items

    if not events:
        logger.info("No events found in the specified time range")
        return []

    logger.info(f"Found {len(events)} events to analyze")

    # 2. Extract log messages from events
    log_messages = _extract_log_messages(events)

    if not log_messages:
        logger.info("No log messages found in events")
        return []

    logger.info(f"Extracted {len(log_messages)} log messages")

    # 3. Deduplicate logs
    unique_logs = deduplicate_texts(log_messages, threshold=params.similarity_threshold)
    logger.info(f"Deduplicated to {len(unique_logs)} unique logs (threshold: {params.similarity_threshold})")

    # 4. Sanitize sensitive data
    sanitized_logs = sanitize_logs(unique_logs)
    logger.info(f"Sanitized {len(sanitized_logs)} logs")

    # Limit batch size
    if len(sanitized_logs) > params.max_logs_per_batch:
        logger.warning(f"Limiting analysis to {params.max_logs_per_batch} logs (total: {len(sanitized_logs)})")
        sanitized_logs = sanitized_logs[: params.max_logs_per_batch]

    # 5. Load system context
    system_context = _load_system_context(context_repository, params.context_types)

    # 6. Analyze logs with AI
    try:
        analysis_result = ai_analyzer.analyze_logs(
            logs=sanitized_logs,
            context=f"Analyzing {len(events)} events from the last {params.lookback_minutes} minutes",
            system_context=system_context,
        )
        logger.info(
            f"AI analysis completed: severity={analysis_result.severity}, "
            f"categories={analysis_result.categories}"
        )
    except Exception as err:
        logger.exception(f"AI analysis failed: {err}")
        return []

    # 7. Check for existing similar analysis (same day)
    today = datetime.utcnow().strftime("%Y-%m-%d")
    analysis_hash = _compute_analysis_hash(analysis_result.patterns, analysis_result.categories)

    existing_analysis = log_analysis_repository.get_by_date_and_hash(today, analysis_hash)

    # Extract event metadata for analysis
    event_ids = [event.id for event in events]
    account = events[0].account if events else "unknown"
    region = events[0].region if events else None

    analyses = []

    if existing_analysis:
        # 8a. Update existing analysis (increment frequency)
        logger.info(f"Found existing analysis for today: {existing_analysis.id}, incrementing frequency")
        log_analysis_repository.increment_frequency(
            date=today,
            analysis_hash=analysis_hash,
            event_ids=event_ids,
        )

        # Reload to get updated frequency
        updated_analysis = log_analysis_repository.get_by_date_and_hash(today, analysis_hash)
        analyses.append(updated_analysis)

    else:
        # 8b. Create new analysis
        logger.info("Creating new log analysis")
        new_analysis = LogAnalysis(
            id=analysis_hash,
            date=today,
            context_ids=list(system_context.keys()) if system_context else [],
            severity=analysis_result.severity,
            categories=analysis_result.categories,
            patterns=analysis_result.patterns,
            frequency=1,
            summary=analysis_result.summary,
            solution=analysis_result.solution,
            log_sample=sanitized_logs[0] if sanitized_logs else "",
            event_ids=event_ids,
            account=account,
            region=region,
        )

        log_analysis_repository.create(new_analysis)
        analyses.append(new_analysis)

    # 9. Link events to analysis (update event records)
    _link_events_to_analysis(events, analysis_hash, event_repository)

    logger.info(f"AI log analysis completed: {len(analyses)} analyses created/updated")
    return analyses


def _extract_log_messages(events: list[Event]) -> list[str]:
    """Extract log messages from events"""
    log_messages = []

    for event in events:
        # Extract message from event detail
        detail = event.detail
        if isinstance(detail, dict):
            # Try common log message fields
            message = (
                detail.get("message")
                or detail.get("log")
                or detail.get("@message")
                or detail.get("msg")
                or str(detail)
            )
            if message:
                log_messages.append(str(message))
        elif isinstance(detail, str):
            log_messages.append(detail)

    return log_messages


def _load_system_context(
    context_repository: ContextRepository,
    context_types: list[str] | None = None,
) -> dict:
    """Load system context for AI understanding"""
    try:
        # Load all contexts or filter by types
        from src.domain.models import ListContextsDTO

        contexts = {}

        if context_types:
            for context_type in context_types:
                dto = ListContextsDTO(context_type=context_type, limit=100)
                result = context_repository.list(dto)
                for ctx in result.items:
                    contexts[ctx.id] = ctx.content
        else:
            # Load all contexts
            dto = ListContextsDTO(limit=100)
            result = context_repository.list(dto)
            for ctx in result.items:
                contexts[ctx.id] = ctx.content

        logger.info(f"Loaded {len(contexts)} system contexts")
        return contexts

    except Exception as err:
        logger.warning(f"Failed to load system context: {err}")
        return {}


def _compute_analysis_hash(patterns: list[str], categories: list[str]) -> str:
    """
    Compute a hash for the analysis to detect duplicates.
    Uses patterns and categories to identify similar issues.
    """
    # Sort to ensure consistent hashing
    sorted_patterns = sorted(patterns)
    sorted_categories = sorted(categories)

    # Combine and hash
    combined = "|".join(sorted_patterns + sorted_categories)
    return hashlib.sha256(combined.encode()).hexdigest()[:16]  # First 16 chars


def _link_events_to_analysis(
    events: list[Event],
    analysis_id: str,
    event_repository: EventRepository,
):
    """Link events to the analysis by updating their analysis_id field"""
    try:
        for event in events:
            if not event.analysis_id:  # Only link if not already linked
                event.analysis_id = analysis_id
                # Note: This requires implementing an update method in EventRepository
                # For now, we'll log it
                logger.debug(f"Would link event {event.id} to analysis {analysis_id}")
                # TODO: Implement event_repository.update(event)
    except Exception as err:
        logger.warning(f"Failed to link events to analysis: {err}")
