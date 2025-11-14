from typing import AsyncIterable

import aioboto3
from types_aioboto3_ecs.client import ECSClient
from types_boto3_ecs.type_defs import ClusterTypeDef

from src.common.constants import AWS_ENDPOINT, AWS_REGION
from src.common.exceptions import InternalServerError
from src.common.meta import SingletonMeta


# Service -----------------------------------
class ECSService(metaclass=SingletonMeta):
    def __init__(self, region=AWS_REGION, endpoint_url=AWS_ENDPOINT):
        self.region = region
        self.endpoint_url = endpoint_url
        self.session = aioboto3.Session()

    async def list_clusters(self, **kwargs) -> AsyncIterable[ClusterTypeDef]:
        """List all ECS clusters."""
        try:
            async with self.session.client("ecs", region_name=self.region, endpoint_url=self.endpoint_url) as client:
                response = await client.list_clusters(**kwargs)

                if cluster_arns := response.get("clusterArns", []):
                    clusters_response = await client.describe_clusters(
                        clusters=cluster_arns, include=["TAGS", "CONFIGURATIONS"]
                    )

                    for cluster in clusters_response.get("clusters", []):
                        yield cluster

                if cursor := response.get("nextToken"):
                    async for cluster in self.list_clusters(nextToken=cursor):
                        yield cluster

        except Exception as e:
            raise InternalServerError(f"An unexpected error occurred while listing ECS clusters: {e}")
