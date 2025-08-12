from typing import Iterable

import boto3
from types_boto3_ecs.client import ECSClient
from types_boto3_ecs.type_defs import ClusterTypeDef

from src.libs.configs import AWS_ENDPOINT, AWS_REGION
from src.libs.exceptions import InternalServerError
from src.libs.meta import SingletonMeta


# Service -----------------------------------
class ECSService(metaclass=SingletonMeta):
    client: ECSClient

    def __init__(self):
        self.client = boto3.client("ecs", endpoint_url=AWS_ENDPOINT, region_name=AWS_REGION)

    def list_monitoring_clusters(self, **kwargs) -> Iterable[ClusterTypeDef]:
        """List all ECS clusters that have tag `monitoring: true`."""
        try:
            response = self.client.list_clusters(**kwargs)

            if cluster_arns := response.get("clusterArns", []):
                clusters = self.client.describe_clusters(clusters=cluster_arns, include=["TAGS", "CONFIGURATIONS"])

                for cluster in clusters.get("clusters", []):
                    # Check if the cluster has the 'monitoring' tag set to 'true'
                    tags = cluster.get("tags", [])
                    if any(tag["key"] == "monitoring" and tag["value"].lower() == "true" for tag in tags):
                        yield cluster

            if cursor := response.get("nextToken"):
                yield from self.list_monitoring_clusters(nextToken=cursor)

        # except self.client.exceptions.ClientException as e:
        #     raise AWSClientException(f"[ClientException] Failed to list ECS clusters: {e}")

        except Exception as e:
            raise InternalServerError(f"An unexpected error occurred while listing ECS clusters: {e}")
