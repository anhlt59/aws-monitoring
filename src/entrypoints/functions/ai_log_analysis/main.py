"""
AI Log Analysis Lambda Function

Scheduled function that runs every 10 minutes to:
1. Query recent events
2. Deduplicate and sanitize logs
3. Analyze with AI
4. Store analysis results
"""

import os

from src.adapters.ai import OpenAILogAnalyzer
from src.adapters.db.repositories import ContextRepository, EventRepository, LogAnalysisRepository
from src.common.logger import logger
from src.domain.use_cases.ai_log_analysis import AILogAnalysisParams, ai_log_analysis_use_case

# Initialize repositories
event_repo = EventRepository()
log_analysis_repo = LogAnalysisRepository()
context_repo = ContextRepository()

# Initialize AI analyzer
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
ai_analyzer = OpenAILogAnalyzer(api_key=openai_api_key, model=openai_model)

# Analysis parameters
lookback_minutes = int(os.getenv("AI_ANALYSIS_LOOKBACK_MINUTES", "10"))
similarity_threshold = float(os.getenv("AI_ANALYSIS_SIMILARITY_THRESHOLD", "0.85"))
max_logs_per_batch = int(os.getenv("AI_ANALYSIS_MAX_LOGS_PER_BATCH", "100"))


@logger.inject_lambda_context(log_event=True)
def handler(event, context):
    """
    Lambda handler for AI log analysis.

    Triggered by EventBridge schedule (every 10 minutes).
    """
    logger.info("AI Log Analysis Lambda triggered")

    try:
        # Build parameters
        params = AILogAnalysisParams(
            lookback_minutes=lookback_minutes,
            similarity_threshold=similarity_threshold,
            max_logs_per_batch=max_logs_per_batch,
            context_types=None,  # Load all context types
        )

        # Run analysis
        analyses = ai_log_analysis_use_case(
            params=params,
            event_repository=event_repo,
            log_analysis_repository=log_analysis_repo,
            context_repository=context_repo,
            ai_analyzer=ai_analyzer,
        )

        logger.info(f"AI log analysis completed successfully: {len(analyses)} analyses created/updated")

        return {
            "statusCode": 200,
            "body": {
                "message": "AI log analysis completed",
                "analyses_count": len(analyses),
                "analyses": [
                    {
                        "id": analysis.id,
                        "date": analysis.date,
                        "severity": analysis.severity,
                        "frequency": analysis.frequency,
                        "summary": analysis.summary,
                    }
                    for analysis in analyses
                ],
            },
        }

    except Exception as err:
        logger.exception(f"Error occurred during AI log analysis: {err}")
        return {
            "statusCode": 500,
            "body": {"message": f"AI log analysis failed: {str(err)}"},
        }
