import json
import os
from typing import Any, Dict, List
from urllib.request import Request, urlopen

from src.common.logger import Logger
from src.domain.master.entities.agent import Agent
from src.domain.master.entities.event import MonitoringEvent
from src.domain.master.ports.notifier import Notifier

logger = Logger(__name__)


class SlackNotifier(Notifier):
    """Slack implementation of Notifier port"""

    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url or os.environ.get("SLACK_WEBHOOK_URL")
        if not self.webhook_url:
            logger.warning("Slack webhook URL not configured")

    async def notify_event(self, event: MonitoringEvent) -> None:
        """Send notification for a monitoring event"""
        try:
            if not self.webhook_url:
                logger.debug("Slack webhook not configured, skipping notification")
                return

            # Format event notification
            color = self._get_severity_color(event.severity.name)

            message = {
                "text": f"🚨 Monitoring Event: {event.detail_type}",
                "attachments": [
                    {
                        "color": color,
                        "fields": [
                            {"title": "Event ID", "value": event.id, "short": True},
                            {"title": "Account", "value": event.account, "short": True},
                            {"title": "Region", "value": event.region, "short": True},
                            {"title": "Source", "value": event.source, "short": True},
                            {"title": "Severity", "value": event.severity.name, "short": True},
                            {
                                "title": "Time",
                                "value": event.published_at.strftime("%Y-%m-%d %H:%M:%S UTC"),
                                "short": True,
                            },
                        ],
                    }
                ],
            }

            # Add resources if available
            if event.resources:
                message["attachments"][0]["fields"].append(
                    {
                        "title": "Resources",
                        "value": "\n".join(event.resources[:3]),  # Limit to first 3
                        "short": False,
                    }
                )

            await self._send_slack_message(message)
            logger.debug(f"Sent Slack notification for event {event.id}")

        except Exception as e:
            logger.error(f"Failed to send Slack notification for event {event.id}: {e}")
            # Don't re-raise as notification failures shouldn't break main flow

    async def notify_agent_status(self, agent: Agent, message: str) -> None:
        """Send notification about agent status change"""
        try:
            if not self.webhook_url:
                logger.debug("Slack webhook not configured, skipping notification")
                return

            # Format agent notification
            status_emoji = self._get_status_emoji(agent.status.value)
            color = self._get_status_color(agent.status.value)

            slack_message = {
                "text": f"{status_emoji} Agent Status Update",
                "attachments": [
                    {
                        "color": color,
                        "fields": [
                            {"title": "Account", "value": agent.account, "short": True},
                            {"title": "Region", "value": agent.region, "short": True},
                            {"title": "Status", "value": agent.status.value, "short": True},
                            {"title": "Message", "value": message, "short": False},
                            {
                                "title": "Updated",
                                "value": agent.updated_at.strftime("%Y-%m-%d %H:%M:%S UTC")
                                if agent.updated_at
                                else "Unknown",
                                "short": True,
                            },
                        ],
                    }
                ],
            }

            await self._send_slack_message(slack_message)
            logger.debug(f"Sent Slack notification for agent {agent.account}")

        except Exception as e:
            logger.error(f"Failed to send Slack notification for agent {agent.account}: {e}")

    async def notify_daily_report(self, report_data: Dict[str, Any]) -> None:
        """Send daily monitoring report"""
        try:
            if not self.webhook_url:
                logger.debug("Slack webhook not configured, skipping notification")
                return

            # Extract key metrics
            event_summary = report_data.get("event_summary", {})
            agent_summary = report_data.get("agent_summary", {})
            recommendations = report_data.get("recommendations", [])

            # Format daily report
            slack_message = {
                "text": f"📊 Daily Monitoring Report - {report_data.get('report_date')}",
                "attachments": [
                    {
                        "color": "good",
                        "fields": [
                            {
                                "title": "Total Events",
                                "value": str(event_summary.get("total_events", 0)),
                                "short": True,
                            },
                            {
                                "title": "Critical Events",
                                "value": str(event_summary.get("critical_events", 0)),
                                "short": True,
                            },
                            {
                                "title": "Healthy Agents",
                                "value": f"{agent_summary.get('healthy_agents', 0)}/{agent_summary.get('total_agents', 0)}",
                                "short": True,
                            },
                            {
                                "title": "Agent Health %",
                                "value": f"{agent_summary.get('health_percentage', 0):.1f}%",
                                "short": True,
                            },
                        ],
                    }
                ],
            }

            # Add recommendations if any
            if recommendations:
                recommendations_text = "\n".join([f"• {rec}" for rec in recommendations[:5]])
                slack_message["attachments"].append(
                    {"color": "warning", "title": "Recommendations", "text": recommendations_text}
                )

            # Add trends if available
            trends = report_data.get("trends", {})
            if trends and "change_percentage" in trends:
                trend_emoji = "📈" if trends["change_percentage"] > 0 else "📉"
                slack_message["attachments"][0]["fields"].append(
                    {
                        "title": f"{trend_emoji} Trend",
                        "value": f"{trends['change_percentage']:+.1f}% vs yesterday",
                        "short": True,
                    }
                )

            await self._send_slack_message(slack_message)
            logger.info("Sent daily report to Slack")

        except Exception as e:
            logger.error(f"Failed to send daily report to Slack: {e}")

    async def notify_critical_alert(self, title: str, message: str, events: List[MonitoringEvent]) -> None:
        """Send critical alert with multiple events"""
        try:
            if not self.webhook_url:
                logger.debug("Slack webhook not configured, skipping notification")
                return

            # Format critical alert
            slack_message = {
                "text": f"🚨🚨 CRITICAL ALERT: {title}",
                "attachments": [
                    {
                        "color": "danger",
                        "text": message,
                        "fields": [
                            {"title": "Event Count", "value": str(len(events)), "short": True},
                            {
                                "title": "Time",
                                "value": events[0].published_at.strftime("%Y-%m-%d %H:%M:%S UTC")
                                if events
                                else "Unknown",
                                "short": True,
                            },
                        ],
                    }
                ],
            }

            # Add details for first few events
            if events:
                event_details = []
                for event in events[:3]:  # Limit to first 3 events
                    event_details.append(f"• {event.source} ({event.account}): {event.detail_type}")

                slack_message["attachments"].append(
                    {"color": "danger", "title": "Affected Events", "text": "\n".join(event_details)}
                )

            await self._send_slack_message(slack_message)
            logger.warning(f"Sent critical alert to Slack: {title}")

        except Exception as e:
            logger.error(f"Failed to send critical alert to Slack: {e}")

    # Helper methods
    async def _send_slack_message(self, message: Dict[str, Any]) -> None:
        """Send message to Slack webhook"""
        try:
            # Prepare request
            data = json.dumps(message).encode("utf-8")
            request = Request(self.webhook_url, data=data, headers={"Content-Type": "application/json"})

            # Send request
            with urlopen(request, timeout=10) as response:
                if response.status != 200:
                    raise Exception(f"Slack API returned status {response.status}")

            logger.debug("Successfully sent message to Slack")

        except Exception as e:
            logger.error(f"Failed to send Slack message: {e}")
            raise

    def _get_severity_color(self, severity: str) -> str:
        """Get Slack color for event severity"""
        color_map = {"CRITICAL": "danger", "HIGH": "danger", "MEDIUM": "warning", "LOW": "good", "UNKNOWN": "#808080"}
        return color_map.get(severity.upper(), "#808080")

    def _get_status_emoji(self, status: str) -> str:
        """Get emoji for agent status"""
        emoji_map = {
            "CREATE_COMPLETE": "✅",
            "UPDATE_COMPLETE": "✅",
            "CREATE_IN_PROGRESS": "🔄",
            "UPDATE_IN_PROGRESS": "🔄",
            "CREATE_FAILED": "❌",
            "UPDATE_FAILED": "❌",
            "DELETE_IN_PROGRESS": "🗑️",
            "DELETE_COMPLETE": "🗑️",
            "DELETE_FAILED": "❌",
        }
        return emoji_map.get(status, "ℹ️")

    def _get_status_color(self, status: str) -> str:
        """Get Slack color for agent status"""
        if "COMPLETE" in status:
            return "good"
        elif "PROGRESS" in status:
            return "warning"
        elif "FAILED" in status:
            return "danger"
        else:
            return "#808080"
