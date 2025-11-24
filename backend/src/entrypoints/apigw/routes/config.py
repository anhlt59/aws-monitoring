"""Configuration API Gateway handlers."""

from http import HTTPStatus

from aws_lambda_powertools.utilities.typing import LambdaContext
from pydantic import BaseModel, Field

from src.domain.use_cases.config import (
    GetAwsConfig,
    GetMonitoringConfig,
    TestAwsConnection,
    UpdateAwsConfig,
    UpdateAwsConfigDTO,
    UpdateMonitoringConfig,
    UpdateMonitoringConfigDTO,
)
from src.entrypoints.apigw.base import create_app
from src.entrypoints.apigw.configs import CORS_ALLOW_ORIGIN, CORS_MAX_AGE
from src.entrypoints.apigw.middleware.auth import get_auth_context

# Create app
app = create_app(
    cors_allow_origin=CORS_ALLOW_ORIGIN,
    cors_max_age=CORS_MAX_AGE,
)

# Initialize use cases
get_aws_config_uc = GetAwsConfig()
update_aws_config_uc = UpdateAwsConfig()
test_aws_connection_uc = TestAwsConnection()
get_monitoring_config_uc = GetMonitoringConfig()
update_monitoring_config_uc = UpdateMonitoringConfig()


# Request models
class UpdateAwsConfigRequest(BaseModel):
    """Update AWS config request model."""

    default_region: str | None = Field(None, description="Default AWS region")
    monitoring_account: str | None = Field(None, description="Monitoring AWS account ID")
    cross_account_role_name: str | None = Field(None, description="Cross-account IAM role name")


class UpdateMonitoringConfigRequest(BaseModel):
    """Update monitoring config request model."""

    query_duration: int | None = Field(None, ge=60, le=3600, description="Query duration in seconds (60-3600)")
    chunk_size: int | None = Field(None, ge=1, le=50, description="Number of log groups per query (1-50)")
    query_string: str | None = Field(None, description="CloudWatch Logs Insights query string")


# API Routes
@app.get("/config/aws")
def get_aws_config():
    """
    Get AWS configuration endpoint.

    Returns singleton AWS configuration.
    Requires admin role.
    """
    # Get auth context and check admin
    auth = get_auth_context(app)
    if not auth.is_admin():
        from aws_lambda_powertools.event_handler.exceptions import UnauthorizedError

        raise UnauthorizedError("Admin role required to view AWS configuration")

    # Execute use case
    config = get_aws_config_uc.execute()

    # Return response
    return config.model_dump(), HTTPStatus.OK


@app.put("/config/aws")
def update_aws_config(request: UpdateAwsConfigRequest):
    """
    Update AWS configuration endpoint.

    Updates singleton AWS configuration.
    Requires admin role.
    """
    # Get auth context and check admin
    auth = get_auth_context(app)
    if not auth.is_admin():
        from aws_lambda_powertools.event_handler.exceptions import UnauthorizedError

        raise UnauthorizedError("Admin role required to update AWS configuration")

    # Create DTO
    dto = UpdateAwsConfigDTO(
        default_region=request.default_region,
        monitoring_account=request.monitoring_account,
        cross_account_role_name=request.cross_account_role_name,
    )

    # Execute use case
    config = update_aws_config_uc.execute(dto)

    # Return response
    return config.model_dump(), HTTPStatus.OK


@app.post("/config/aws/test")
def test_aws_connection():
    """
    Test AWS connection endpoint.

    Validates AWS credentials and permissions.
    Requires admin role.
    """
    # Get auth context and check admin
    auth = get_auth_context(app)
    if not auth.is_admin():
        from aws_lambda_powertools.event_handler.exceptions import UnauthorizedError

        raise UnauthorizedError("Admin role required to test AWS connection")

    # Execute use case
    result = test_aws_connection_uc.execute()

    # Return response with appropriate status code
    status_code = HTTPStatus.OK if result.success else HTTPStatus.BAD_REQUEST

    return result.model_dump(), status_code


@app.get("/config/monitoring")
def get_monitoring_config():
    """
    Get monitoring configuration endpoint.

    Returns singleton monitoring configuration.
    Requires admin role.
    """
    # Get auth context and check admin
    auth = get_auth_context(app)
    if not auth.is_admin():
        from aws_lambda_powertools.event_handler.exceptions import UnauthorizedError

        raise UnauthorizedError("Admin role required to view monitoring configuration")

    # Execute use case
    config = get_monitoring_config_uc.execute()

    # Return response
    return config.model_dump(), HTTPStatus.OK


@app.put("/config/monitoring")
def update_monitoring_config(request: UpdateMonitoringConfigRequest):
    """
    Update monitoring configuration endpoint.

    Updates singleton monitoring configuration.
    Requires admin role.
    """
    # Get auth context and check admin
    auth = get_auth_context(app)
    if not auth.is_admin():
        from aws_lambda_powertools.event_handler.exceptions import UnauthorizedError

        raise UnauthorizedError("Admin role required to update monitoring configuration")

    # Create DTO
    dto = UpdateMonitoringConfigDTO(
        query_duration=request.query_duration,
        chunk_size=request.chunk_size,
        query_string=request.query_string,
    )

    # Execute use case
    config = update_monitoring_config_uc.execute(dto)

    # Return response
    return config.model_dump(), HTTPStatus.OK


# Lambda handler
def handler(event: dict, context: LambdaContext) -> dict:
    """Lambda function handler for config endpoints."""
    return app.resolve(event, context)
