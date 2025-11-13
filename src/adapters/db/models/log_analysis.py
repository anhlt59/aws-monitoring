from pynamodb.attributes import ListAttribute, NumberAttribute, UnicodeAttribute

from .base import DynamoModel, KeyAttribute


class LogAnalysisPersistence(DynamoModel, discriminator="LOG_ANALYSIS"):
    """
    Store AI-powered log analysis results.
    Each analysis represents a unique pattern/issue identified in logs for a specific day.
    """

    # Keys
    pk = KeyAttribute(hash_key=True, default="LOG_ANALYSIS")
    sk = KeyAttribute(
        range_key=True, prefix="LOG_ANALYSIS#"
    )  # LOG_ANALYSIS#{date}#{analysis_hash}  # e.g., LOG_ANALYSIS#2024-01-15#abc123

    # Attributes
    date = UnicodeAttribute(null=False)  # YYYY-MM-DD format for daily grouping
    analysis_hash = UnicodeAttribute(null=False)  # Hash of the pattern for deduplication
    context_ids = ListAttribute(null=True, default=lambda: [])  # Links to context schema for better AI understanding

    # Analysis Results
    severity = NumberAttribute(null=False, default=0)  # 0=Unknown, 1=Low, 2=Medium, 3=High, 4=Critical
    categories = ListAttribute(null=True, default=lambda: [])  # e.g., ["Database", "Connection", "Timeout"]
    patterns = ListAttribute(null=True, default=lambda: [])  # List of identified patterns
    frequency = NumberAttribute(null=False, default=1)  # Count of similar logs in the same day
    summary = UnicodeAttribute(null=False)  # Concise summary of the issue
    solution = UnicodeAttribute(null=True)  # Recommended solution or action
    log_sample = UnicodeAttribute(null=False)  # Sample log entry for reference

    # Related entities
    event_ids = ListAttribute(null=True, default=lambda: [])  # Links to related event IDs
    account = UnicodeAttribute(null=False)  # AWS Account ID
    region = UnicodeAttribute(null=True)  # AWS Region

    # Metadata
    analyzed_at = NumberAttribute(null=False)  # Unix timestamp of analysis
    updated_at = NumberAttribute(null=False)  # Last update timestamp
