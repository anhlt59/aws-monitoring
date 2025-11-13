"""Port interface for AI log analysis services"""

from typing import Protocol

from pydantic import BaseModel


class LogAnalysisResult(BaseModel):
    """Result from AI log analysis"""

    severity: int  # 0=Unknown, 1=Low, 2=Medium, 3=High, 4=Critical
    categories: list[str]  # e.g., ["Database", "Connection", "Timeout"]
    patterns: list[str]  # Identified patterns
    summary: str  # Concise summary
    solution: str | None = None  # Recommended solution


class IAILogAnalyzer(Protocol):
    """Interface for AI-powered log analysis services"""

    def analyze_logs(
        self,
        logs: list[str],
        context: str | None = None,
        system_context: dict | None = None,
    ) -> LogAnalysisResult:
        """
        Analyze logs using AI to identify patterns, severity, and solutions.

        Args:
            logs: List of log messages to analyze (already deduplicated and sanitized)
            context: Optional additional context about the logs
            system_context: Optional system context (architecture, tech stack, etc.)

        Returns:
            LogAnalysisResult with severity, categories, patterns, summary, and solution
        """
        ...
