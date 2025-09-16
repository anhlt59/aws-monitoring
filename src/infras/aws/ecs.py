from typing import Iterable

import boto3
from types_boto3_ecs.client import ECSClient
from types_boto3_ecs.type_defs import ClusterTypeDef

from src.common.constants import AWS_ENDPOINT, AWS_REGION
from src.common.exceptions import InternalServerError
from src.common.meta import SingletonMeta


# Service -----------------------------------
class ECSService(metaclass=SingletonMeta):
    client: ECSClient

    def __init__(self, region=AWS_REGION, endpoint_url=AWS_ENDPOINT):
        self.client = boto3.client("ecs", region_name=region, endpoint_url=endpoint_url)

    def list_clusters_by_tag(self, tag_name: str, tag_value: str, **kwargs) -> Iterable[ClusterTypeDef]:
        """List all ECS clusters."""
        try:
            response = self.client.list_clusters(**kwargs)

            if cluster_arns := response.get("clusterArns", []):
                clusters = self.client.describe_clusters(clusters=cluster_arns, include=["TAGS", "CONFIGURATIONS"])

                for cluster in clusters:
                    for tag in cluster.get("tags", []):
                        if tag.get("key") == tag_name and tag.get("value", "") == tag_value:
                            yield cluster

            if cursor := response.get("nextToken"):
                yield from self.list_clusters(tag_name, tag_value, nextToken=cursor)

        except Exception as e:
            raise InternalServerError(f"An unexpected error occurred while listing ECS clusters: {e}")
