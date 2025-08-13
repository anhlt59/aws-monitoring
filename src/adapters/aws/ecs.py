from typing import Iterable

import boto3
from types_boto3_ecs.client import ECSClient
from types_boto3_ecs.type_defs import ClusterTypeDef

from src.common.configs import AWS_ENDPOINT, AWS_REGION
from src.common.exceptions import AWSClientException, InternalServerError
from src.common.meta import SingletonMeta


# Service -----------------------------------
class ECSService(metaclass=SingletonMeta):
    client: ECSClient

    def __init__(self):
        self.client = boto3.client("ecs", endpoint_url=AWS_ENDPOINT, region_name=AWS_REGION)

    def list_monitoring_clusters(self, next_token: str | None = None) -> Iterable[ClusterTypeDef]:
        """List all ECS clusters that have tag `monitoring: true`."""
        try:
            response = self.client.list_clusters(nextToken=next_token)

            if cluster_arns := response.get("clusterArns", []):
                clusters = self.client.describe_clusters(clusters=cluster_arns)

                for cluster in clusters.get("clusters", []):
                    tags = cluster.get("tags", [])
                    if any(tag["key"].lower() == "monitoring" and tag["value"].lower() == "true" for tag in tags):
                        yield cluster

            if next_token := response.get("nextToken"):
                yield from self.list_monitoring_clusters(next_token=next_token)

        except self.client.exceptions.ClientException as e:
            raise AWSClientException(f"[ClientException] Failed to list ECS clusters: {e}")

        except Exception as e:
            raise InternalServerError(f"An unexpected error occurred while listing ECS clusters: {e}")
