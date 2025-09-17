import json
from typing import Any, Dict

from src.adapters.container import container
from src.common.logger import Logger
from src.domain.master.dtos.agent_dtos import AgentDeploymentRequestDTO

logger = Logger(__name__)


def handler(event: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """AWS Lambda handler for managing agent deployments"""
    try:
        logger.info(f"Processing deployment request: {event}")

        # Get use case from container
        use_case = container.resolve("update_deployment_use_case")

        # Determine operation type
        operation = event.get("operation", "deploy")

        if operation == "deploy":
            return await _handle_deployment(use_case, event)
        elif operation == "complete":
            return await _handle_completion(use_case, event)
        elif operation == "status":
            return await _handle_status(use_case, event)
        elif operation == "delete":
            return await _handle_deletion(use_case, event)
        else:
            raise ValueError(f"Unknown operation: {operation}")

    except Exception as e:
        logger.error(f"Failed to process deployment request: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"status": "error", "message": str(e)}),
        }


async def _handle_deployment(use_case, event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle deployment initiation"""
    try:
        # Create deployment request DTO
        request_dto = AgentDeploymentRequestDTO(
            account=event["account"],
            region=event["region"],
            stack_name=event.get("stack_name", f"monitoring-agent-{event['account']}"),
            parameters=event.get("parameters", {}),
        )

        # Execute deployment
        agent = await use_case.execute(request_dto)

        logger.info(f"Deployment initiated for account {agent.account}")

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "status": "success",
                    "operation": "deploy",
                    "account": agent.account,
                    "agent_status": agent.status.value,
                }
            ),
        }

    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        raise


async def _handle_completion(use_case, event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle deployment completion"""
    try:
        account = event["account"]
        success = event.get("success", True)

        # Mark deployment as completed
        agent = await use_case.complete_deployment(account=account, success=success)

        status_msg = "completed" if success else "failed"
        logger.info(f"Deployment {status_msg} for account {account}")

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "status": "success",
                    "operation": "complete",
                    "account": agent.account,
                    "agent_status": agent.status.value,
                    "deployment_success": success,
                }
            ),
        }

    except Exception as e:
        logger.error(f"Failed to complete deployment: {e}")
        raise


async def _handle_status(use_case, event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle agent status check"""
    try:
        account = event["account"]

        # Get agent health
        health = await use_case.get_agent_health(account)

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "status": "success",
                    "operation": "status",
                    "agent": {
                        "account": health.account,
                        "region": health.region,
                        "status": health.status.value,
                        "is_healthy": health.is_healthy,
                        "is_operational": health.is_operational,
                        "deployed_at": health.deployed_at.isoformat(),
                        "last_heartbeat": (health.last_heartbeat.isoformat() if health.last_heartbeat else None),
                    },
                }
            ),
        }

    except Exception as e:
        logger.error(f"Failed to get agent status: {e}")
        raise


async def _handle_deletion(use_case, event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle agent deletion"""
    try:
        account = event["account"]

        # Delete agent
        success = await use_case.delete_agent(account)

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "status": "success",
                    "operation": "delete",
                    "account": account,
                    "deleted": success,
                }
            ),
        }

    except Exception as e:
        logger.error(f"Failed to delete agent: {e}")
        raise
