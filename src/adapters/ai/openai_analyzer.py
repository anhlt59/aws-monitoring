"""OpenAI-based log analyzer implementation"""

import json
import os
from typing import Any

from openai import OpenAI

from src.common.logger import logger
from src.domain.ports.ai_analyzer import IAILogAnalyzer, LogAnalysisResult


class OpenAILogAnalyzer(IAILogAnalyzer):
    """OpenAI GPT-based log analyzer"""

    def __init__(self, api_key: str | None = None, model: str = "gpt-4o-mini", temperature: float = 0.3):
        """
        Initialize OpenAI analyzer.

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: Model to use (default: gpt-4o-mini for cost efficiency)
            temperature: Temperature for generation (0.0-1.0, lower = more focused)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required (set OPENAI_API_KEY env var)")

        self.model = model
        self.temperature = temperature
        self.client = OpenAI(api_key=self.api_key)

    def analyze_logs(
        self,
        logs: list[str],
        context: str | None = None,
        system_context: dict | None = None,
    ) -> LogAnalysisResult:
        """
        Analyze logs using OpenAI GPT to identify patterns, severity, and solutions.

        Args:
            logs: List of log messages (already deduplicated and sanitized)
            context: Optional additional context
            system_context: Optional system context

        Returns:
            LogAnalysisResult with analysis results
        """
        if not logs:
            raise ValueError("No logs provided for analysis")

        # Build the prompt
        prompt = self._build_prompt(logs, context, system_context)

        try:
            # Call OpenAI API with structured output
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert DevOps engineer analyzing application logs. "
                            "Analyze the provided logs and identify patterns, severity, categories, "
                            "and provide actionable solutions. Be concise but thorough."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=self.temperature,
                response_format={"type": "json_object"},
            )

            # Parse response
            result_text = response.choices[0].message.content
            result_dict = json.loads(result_text)

            logger.info(f"OpenAI analysis completed. Model: {self.model}, Tokens: {response.usage.total_tokens}")

            return self._parse_result(result_dict)

        except Exception as err:
            logger.exception(f"OpenAI log analysis failed: {err}")
            # Return a fallback result
            return LogAnalysisResult(
                severity=0,
                categories=["Error"],
                patterns=["Analysis failed"],
                summary=f"Failed to analyze logs: {str(err)}",
                solution="Please retry or check logs manually",
            )

    def _build_prompt(self, logs: list[str], context: str | None, system_context: dict | None) -> str:
        """Build the analysis prompt"""
        prompt_parts = [
            "Analyze the following application logs and provide structured analysis.\n",
        ]

        # Add system context if available
        if system_context:
            prompt_parts.append("## System Context\n")
            prompt_parts.append(json.dumps(system_context, indent=2))
            prompt_parts.append("\n\n")

        # Add additional context if available
        if context:
            prompt_parts.append(f"## Additional Context\n{context}\n\n")

        # Add logs
        prompt_parts.append("## Logs to Analyze\n")
        for i, log in enumerate(logs[:50], 1):  # Limit to 50 logs to avoid token limits
            prompt_parts.append(f"{i}. {log}\n")

        if len(logs) > 50:
            prompt_parts.append(f"\n... and {len(logs) - 50} more similar logs\n")

        # Add instructions
        prompt_parts.append(
            "\n## Instructions\n"
            "Provide analysis in JSON format with the following structure:\n"
            "{\n"
            '  "severity": <int 0-4>,  // 0=Unknown, 1=Low, 2=Medium, 3=High, 4=Critical\n'
            '  "categories": [<string>],  // e.g., ["Database", "Connection", "Timeout"]\n'
            '  "patterns": [<string>],  // Identified patterns in the logs\n'
            '  "summary": <string>,  // 2-3 sentence summary of the issue\n'
            '  "solution": <string>  // Recommended solution or action (optional)\n'
            "}\n\n"
            "Guidelines:\n"
            "- Identify the root cause and common patterns\n"
            "- Categorize the issue (e.g., Database, Network, Application, Infrastructure)\n"
            "- Assign appropriate severity based on impact\n"
            "- Provide actionable solutions when possible\n"
            "- Be concise but specific\n"
        )

        return "".join(prompt_parts)

    def _parse_result(self, result_dict: dict[str, Any]) -> LogAnalysisResult:
        """Parse and validate the API result"""
        return LogAnalysisResult(
            severity=int(result_dict.get("severity", 0)),
            categories=result_dict.get("categories", []),
            patterns=result_dict.get("patterns", []),
            summary=result_dict.get("summary", "No summary provided"),
            solution=result_dict.get("solution"),
        )
