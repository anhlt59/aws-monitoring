"""
Sensitive data sanitization utilities for log analysis.
Removes or masks sensitive information before sending to AI services.
"""

import re


# Regex patterns for sensitive data
PATTERNS = {
    # AWS credentials
    "aws_access_key": (
        r"(?:A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}",
        "[AWS_ACCESS_KEY]",
    ),
    "aws_secret_key": (r"(?i)aws(.{0,20})?(?-i)['\"][0-9a-zA-Z/+]{40}['\"]", "[AWS_SECRET_KEY]"),
    # IP addresses
    "ipv4": (r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", "[IP_ADDRESS]"),
    "ipv6": (r"\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b", "[IP_ADDRESS]"),
    # Email addresses
    "email": (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[EMAIL]"),
    # Phone numbers (basic patterns)
    "phone": (r"\b(?:\+?1[-.]?)?\(?[0-9]{3}\)?[-.]?[0-9]{3}[-.]?[0-9]{4}\b", "[PHONE]"),
    # Credit card numbers (basic pattern)
    "credit_card": (r"\b(?:\d{4}[-\s]?){3}\d{4}\b", "[CREDIT_CARD]"),
    # Social Security Numbers
    "ssn": (r"\b\d{3}-\d{2}-\d{4}\b", "[SSN]"),
    # API keys (generic pattern)
    "api_key": (r"(?i)(api[_-]?key|apikey)[\s:=]+['\"]?([a-zA-Z0-9_\-]{20,})['\"]?", "[API_KEY]"),
    # Bearer tokens
    "bearer_token": (r"(?i)bearer[\s]+([a-zA-Z0-9_\-\.=]+)", "[BEARER_TOKEN]"),
    # JWT tokens (basic pattern)
    "jwt": (r"eyJ[A-Za-z0-9_-]*\.eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*", "[JWT_TOKEN]"),
    # Passwords in common formats
    "password": (r"(?i)(password|passwd|pwd)[\s:=]+['\"]?([^\s'\"]+)['\"]?", "[PASSWORD]"),
    # Database connection strings
    "connection_string": (
        r"(?i)(mongodb|mysql|postgresql|postgres)://[^\s]+:[^\s]+@[^\s]+",
        "[DB_CONNECTION_STRING]",
    ),
}


def sanitize_text(text: str, patterns: dict[str, tuple[str, str]] | None = None) -> str:
    """
    Remove sensitive information from text.

    Args:
        text: Text to sanitize
        patterns: Custom patterns dict {name: (regex, replacement)}
                 If None, uses default PATTERNS

    Returns:
        Sanitized text with sensitive info replaced
    """
    if not text:
        return text

    patterns_to_use = patterns or PATTERNS
    sanitized = text

    for pattern_name, (regex, replacement) in patterns_to_use.items():
        try:
            sanitized = re.sub(regex, replacement, sanitized)
        except re.error:
            # Skip invalid regex patterns
            continue

    return sanitized


def sanitize_dict(data: dict, patterns: dict[str, tuple[str, str]] | None = None) -> dict:
    """
    Recursively sanitize all string values in a dictionary.

    Args:
        data: Dictionary to sanitize
        patterns: Custom patterns dict

    Returns:
        Sanitized dictionary
    """
    if not isinstance(data, dict):
        return data

    sanitized = {}
    for key, value in data.items():
        if isinstance(value, str):
            sanitized[key] = sanitize_text(value, patterns)
        elif isinstance(value, dict):
            sanitized[key] = sanitize_dict(value, patterns)
        elif isinstance(value, list):
            sanitized[key] = [sanitize_dict(item, patterns) if isinstance(item, dict) else item for item in value]
        else:
            sanitized[key] = value

    return sanitized


def sanitize_log_entry(log_entry: str | dict, patterns: dict[str, tuple[str, str]] | None = None) -> str | dict:
    """
    Sanitize a log entry (string or dict).

    Args:
        log_entry: Log entry to sanitize
        patterns: Custom patterns dict

    Returns:
        Sanitized log entry
    """
    if isinstance(log_entry, dict):
        return sanitize_dict(log_entry, patterns)
    elif isinstance(log_entry, str):
        return sanitize_text(log_entry, patterns)
    else:
        return log_entry


def sanitize_logs(logs: list[str | dict], patterns: dict[str, tuple[str, str]] | None = None) -> list[str | dict]:
    """
    Sanitize a list of log entries.

    Args:
        logs: List of log entries to sanitize
        patterns: Custom patterns dict

    Returns:
        List of sanitized log entries
    """
    return [sanitize_log_entry(log, patterns) for log in logs]
