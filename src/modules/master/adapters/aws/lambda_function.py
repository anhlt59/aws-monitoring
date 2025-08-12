from typing import Iterable

import boto3
from types_boto3_lambda.client import LambdaClient
from types_boto3_lambda.type_defs import FunctionConfigurationTypeDef

from src.libs.configs import AWS_ENDPOINT, AWS_REGION
from src.libs.exceptions import InternalServerError
from src.libs.meta import SingletonMeta


# Service -----------------------------------
class LambdaService(metaclass=SingletonMeta):
    client: LambdaClient

    def __init__(self):
        self.client = boto3.client("lambda", endpoint_url=AWS_ENDPOINT, region_name=AWS_REGION)

    def list_monitoring_functions(self, **kwargs) -> Iterable[FunctionConfigurationTypeDef]:
        """List all Lambda functions that have tag `monitoring: true`."""
        try:
            response = self.client.list_functions(**kwargs)

            for function in response.get("Functions", []):
                # Check if the function has the 'monitoring' tag set to 'true'
                tags = self.client.list_tags(Resource=function["FunctionArn"]).get("Tags", {})
                if tags.get("monitoring", "").lower() == "true":
                    yield function

            if cursor := response.get("NextMarker"):
                yield from self.list_monitoring_functions(Marker=cursor)

        # except self.client.exceptions.ClientError as e:
        #     raise AWSClientException(f"[ClientException] Failed to list Lambda functions: {e}")

        except Exception as e:
            raise InternalServerError(f"An unexpected error occurred while listing Lambda functions: {e}")
