"""Test AWS connection use case."""

from pydantic import Field

from src.common.models import BaseModel


class TestConnectionResultDTO(BaseModel):
    """Test connection result."""

    success: bool = Field(..., description="Whether connection was successful")
    message: str = Field(..., description="Result message")
    details: dict | None = Field(None, description="Additional details")


class TestAwsConnection:
    """
    Use case for testing AWS connection.

    Validates AWS credentials and permissions.
    Requires admin permissions.
    """

    def execute(self) -> TestConnectionResultDTO:
        """
        Test AWS connection.

        Returns:
            TestConnectionResultDTO with connection test result
        """
        try:
            # Try to connect to AWS
            import boto3

            # Create STS client to verify credentials
            sts_client = boto3.client("sts")

            # Get caller identity
            identity = sts_client.get_caller_identity()

            return TestConnectionResultDTO(
                success=True,
                message="AWS connection successful",
                details={
                    "account": identity.get("Account"),
                    "user_id": identity.get("UserId"),
                    "arn": identity.get("Arn"),
                },
            )

        except Exception as e:
            return TestConnectionResultDTO(
                success=False,
                message=f"AWS connection failed: {str(e)}",
                details=None,
            )
