"""
Enums for event types, states, and notification configurations.

This module centralizes magic strings into type-safe enums for better
maintainability and IDE support.
"""

from enum import Enum


class AlarmState(str, Enum):
    """CloudWatch Alarm states with emoji and color mappings."""

    ALARM = "ALARM"
    OK = "OK"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"

    def emoji(self) -> str:
        """Get emoji representation for alarm state."""
        return {
            self.ALARM: ":red_circle:",
            self.OK: ":recycle:",
            self.INSUFFICIENT_DATA: ":heavy_exclamation_mark:",
        }.get(self, ":grey_question:")

    def color(self) -> str:
        """Get hex color code for alarm state."""
        return {
            self.ALARM: "#FF0000",  # Red
            self.OK: "#36A64F",  # Green
            self.INSUFFICIENT_DATA: "#FFA500",  # Orange
        }.get(self, "#CCCCCC")  # Grey default


class HealthEventCategory(str, Enum):
    """AWS Health event type categories."""

    ISSUE = "issue"
    ACCOUNT_NOTIFICATION = "accountnotification"
    SCHEDULED_CHANGE = "scheduledchange"

    def emoji(self) -> str:
        """Get emoji representation for health event category."""
        return {
            self.ISSUE: ":warning:",
            self.ACCOUNT_NOTIFICATION: ":information_source:",
            self.SCHEDULED_CHANGE: ":calendar:",
        }.get(self, ":grey_question:")


class HealthEventStatus(str, Enum):
    """AWS Health event status codes."""

    OPEN = "open"
    CLOSED = "closed"
    UPCOMING = "upcoming"

    def color(self) -> str:
        """Get hex color code for health event status."""
        return {
            self.OPEN: "#FFA500",  # Orange
            self.CLOSED: "#36A64F",  # Green
            self.UPCOMING: "#439FE0",  # Blue
        }.get(self, "#CCCCCC")  # Grey default


class SeverityLevel(str, Enum):
    """Security finding severity levels."""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

    @classmethod
    def from_score(cls, score: float) -> "SeverityLevel":
        """
        Determine severity level from numeric score.

        Args:
            score: Numeric severity score (typically 0-10 for GuardDuty)

        Returns:
            Corresponding SeverityLevel enum value
        """
        if score >= 7:
            return cls.HIGH
        elif score >= 4:
            return cls.MEDIUM
        else:
            return cls.LOW

    def color(self) -> str:
        """Get hex color code for severity level."""
        return {
            self.HIGH: "#FF0000",  # Red
            self.MEDIUM: "#FFA500",  # Orange
            self.LOW: "#36A64F",  # Green
        }.get(self, "#CCCCCC")  # Grey default


class CfnStackStatusType(str, Enum):
    """CloudFormation stack status types with emoji and color mappings."""

    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    WARNING = "WARNING"

    def emoji(self) -> str:
        """Get emoji representation for CloudFormation stack status."""
        return {
            self.SUCCESS: ":rocket:",
            self.FAILURE: ":x:",
            self.WARNING: ":warning:",
        }.get(self, ":grey_question:")

    def color(self) -> str:
        """Get hex color code for CloudFormation stack status."""
        return {
            self.SUCCESS: "#36A64F",  # Green
            self.FAILURE: "#FF0000",  # Red
            self.WARNING: "#FFA500",  # Orange
        }.get(self, "#CCCCCC")  # Grey default


class EventSource(str, Enum):
    """Event source identifiers for routing and processing."""

    # AWS native sources
    AWS_HEALTH = "aws.health"
    AWS_GUARDDUTY = "aws.guardduty"
    AWS_CLOUDWATCH = "aws.cloudwatch"
    AWS_CLOUDFORMATION = "aws.cloudformation"

    # Monitoring agent sources
    AGENT_HEALTH = "monitoring.agent.health"
    AGENT_GUARDDUTY = "monitoring.agent.guardduty"
    AGENT_CLOUDWATCH = "monitoring.agent.cloudwatch"
    AGENT_LOGS = "monitoring.agent.logs"
    AGENT_CLOUDFORMATION = "monitoring.agent.cloudformation"


__all__ = [
    "AlarmState",
    "HealthEventCategory",
    "HealthEventStatus",
    "SeverityLevel",
    "CfnStackStatusType",
    "EventSource",
]
