from datetime import UTC, datetime, timedelta
from typing import Any, Dict, List

from src.common.logger import logger
from src.domain.master.dtos.event_dtos import EventSummaryDTO
from src.domain.master.entities.agent import Agent
from src.domain.master.entities.event import MonitoringEvent
from src.domain.master.ports.agent_repository import AgentRepository
from src.domain.master.ports.event_repository import EventRepository
from src.domain.master.ports.notifier import Notifier
from src.domain.master.value_objects.severity import Severity




class GenerateDailyReportUseCase:
    """Use case for generating daily monitoring reports"""

    def __init__(
        self,
        event_repository: EventRepository,
        agent_repository: AgentRepository,
        notifier: Notifier,
    ):
        self.event_repository = event_repository
        self.agent_repository = agent_repository
        self.notifier = notifier

    async def execute(self, report_date: datetime = None) -> Dict[str, Any]:
        """Generate and send daily monitoring report"""
        if not report_date:
            report_date = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)

        try:
            logger.info(f"Generating daily report for {report_date.date()}")

            # Calculate report time range (previous 24 hours)
            start_time = report_date - timedelta(days=1)
            end_time = report_date

            # Gather data for report
            events = await self.event_repository.find_by_time_range(start_time=start_time, end_time=end_time)
            agents = await self.agent_repository.find_all()

            # Generate report data
            report_data = await self._generate_report_data(events, agents, start_time, end_time)

            # Send report notification
            await self.notifier.notify_daily_report(report_data)

            logger.info(f"Daily report generated successfully with {len(events)} events")
            return report_data

        except Exception as e:
            logger.error(f"Failed to generate daily report: {e}")
            raise

    async def _generate_report_data(
        self,
        events: List[MonitoringEvent],
        agents: List[Agent],
        start_time: datetime,
        end_time: datetime,
    ) -> Dict[str, Any]:
        """Generate comprehensive report data"""

        # Event statistics
        event_summary = self._calculate_event_summary(events, start_time, end_time)

        # Agent health summary
        agent_summary = self._calculate_agent_summary(agents)

        # Top issues
        top_issues = self._identify_top_issues(events)

        # Critical events
        critical_events = [event for event in events if event.is_critical()]

        # Trends (compare with previous day if possible)
        trends = await self._calculate_trends(start_time, end_time)

        return {
            "report_date": start_time.date().isoformat(),
            "time_range": {"start": start_time.isoformat(), "end": end_time.isoformat()},
            "event_summary": event_summary.model_dump(),
            "agent_summary": agent_summary,
            "critical_events": [
                {
                    "id": event.id,
                    "source": event.source,
                    "severity": event.severity.name,
                    "account": event.account,
                    "resources": event.resources,
                    "published_at": event.published_at.isoformat(),
                }
                for event in critical_events[:10]  # Limit to top 10
            ],
            "top_issues": top_issues,
            "trends": trends,
            "recommendations": self._generate_recommendations(events, agents),
        }

    def _calculate_event_summary(
        self, events: List[MonitoringEvent], start_time: datetime, end_time: datetime
    ) -> EventSummaryDTO:
        """Calculate event statistics"""
        severity_counts = {severity: 0 for severity in Severity}

        for event in events:
            severity_counts[event.severity] += 1

        return EventSummaryDTO(
            total_events=len(events),
            critical_events=severity_counts[Severity.CRITICAL],
            high_events=severity_counts[Severity.HIGH],
            medium_events=severity_counts[Severity.MEDIUM],
            low_events=severity_counts[Severity.LOW],
            unknown_events=severity_counts[Severity.UNKNOWN],
            time_range={"start": start_time.isoformat(), "end": end_time.isoformat()},
        )

    def _calculate_agent_summary(self, agents: List[Agent]) -> Dict[str, Any]:
        """Calculate agent health statistics"""
        total_agents = len(agents)
        healthy_agents = len([agent for agent in agents if agent.is_healthy()])
        operational_agents = len([agent for agent in agents if agent.is_operational()])
        failed_agents = len([agent for agent in agents if agent.has_deployment_failed()])

        return {
            "total_agents": total_agents,
            "healthy_agents": healthy_agents,
            "operational_agents": operational_agents,
            "failed_agents": failed_agents,
            "health_percentage": (healthy_agents / total_agents * 100) if total_agents > 0 else 0,
        }

    def _identify_top_issues(self, events: List[MonitoringEvent]) -> List[Dict[str, Any]]:
        """Identify most common issues"""
        # Group by source and count
        source_counts = {}
        for event in events:
            if event.is_critical():
                source_counts[event.source] = source_counts.get(event.source, 0) + 1

        # Sort by frequency and return top 5
        top_sources = sorted(source_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        return [{"source": source, "count": count} for source, count in top_sources]

    async def _calculate_trends(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Calculate trends compared to previous period"""
        # Previous day events for comparison
        prev_start = start_time - timedelta(days=1)
        prev_end = start_time

        try:
            prev_events = await self.event_repository.find_by_time_range(start_time=prev_start, end_time=prev_end)

            current_count = await self.event_repository.count_by_time_range(start_time=start_time, end_time=end_time)
            previous_count = len(prev_events)

            change_percentage = ((current_count - previous_count) / previous_count * 100) if previous_count > 0 else 0

            return {
                "current_events": current_count,
                "previous_events": previous_count,
                "change_percentage": round(change_percentage, 2),
                "trend": "increasing" if change_percentage > 0 else "decreasing",
            }

        except Exception as e:
            logger.warning(f"Could not calculate trends: {e}")
            return {"error": "Trend calculation unavailable"}

    def _generate_recommendations(self, events: List[MonitoringEvent], agents: List[Agent]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # Check for high error rates
        critical_count = len([e for e in events if e.is_critical()])
        if critical_count > 10:
            recommendations.append(
                f"High number of critical events ({critical_count}). Consider reviewing affected systems."
            )

        # Check agent health
        failed_agents = [agent for agent in agents if agent.has_deployment_failed()]
        if failed_agents:
            recommendations.append(
                f"{len(failed_agents)} agent(s) have failed deployment. Check CloudFormation stacks."
            )

        # Check for repeated issues
        sources = [event.source for event in events if event.is_critical()]
        if len(set(sources)) < len(sources) * 0.5:  # More than 50% from same sources
            recommendations.append("Repeated issues from same sources detected. Consider automated remediation.")

        return recommendations if recommendations else ["No specific recommendations at this time."]
