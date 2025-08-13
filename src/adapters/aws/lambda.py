import boto3
from types_boto3_lambda.client import LambdaClient

from src.common.configs import AWS_ENDPOINT, AWS_REGION
from src.common.meta import SingletonMeta


# Service -----------------------------------
class LambdaService(metaclass=SingletonMeta):
    client: LambdaClient

    def __init__(self):
        self.client = boto3.client("lambda", endpoint_url=AWS_ENDPOINT, region_name=AWS_REGION)

    # def list_monitoring_clusters(self) -> Iterable[]:
    #     """List all Lambda clusters that have tag `monitoring: true`."""
    #     try:
    #         pass
    #         # response = self.client.list_functions()
    #         #
    #         # if cluster_arns := response.get("clusterArns", []):
    #         #     clusters = self.client.describe_clusters(clusters=cluster_arns)
    #         #
    #         #     for cluster in clusters.get("clusters", []):
    #         #         tags = cluster.get("tags", [])
    #         #         if any(tag["key"].lower() == "monitoring" and tag["value"].lower() == "true" for tag in tags):
    #         #             yield cluster
    #
    #     except self.client.exceptions.ClientException as e:
    #         raise AWSClientException(f"[ClientException] Failed to list Lambda clusters: {e}")
    #
    #     except Exception as e:
    #         raise InternalServerError(f"An unexpected error occurred while listing Lambda clusters: {e}")
