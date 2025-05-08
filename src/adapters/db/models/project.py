from pynamodb.attributes import UnicodeAttribute
from pynamodb.indexes import AllProjection, GlobalSecondaryIndex

from .base import DynamoMeta, DynamoModel, KeyAttribute


class GSI1Index(GlobalSecondaryIndex):
    class Meta(DynamoMeta):
        index_name = "gsi1"
        projection = AllProjection()

    gsi1pk = KeyAttribute(hash_key=True, default="PROJECT")
    gsi1sk = KeyAttribute(range_key=True, prefix="NAME#")


class ProjectPersistence(DynamoModel, discriminator="PROJECT"):
    # Keys
    pk = KeyAttribute(hash_key=True, prefix="PROJECT#")
    sk = KeyAttribute(range_key=True, default="METADATA")
    # Index
    gsi1 = GSI1Index()
    gsi1pk = KeyAttribute(default="PROJECT")
    gsi1sk = KeyAttribute(prefix="NAME#", null=False)
    # Attributes
    name = UnicodeAttribute(null=False)
    description = UnicodeAttribute(null=False)
