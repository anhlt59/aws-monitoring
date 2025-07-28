from pynamodb.attributes import ListAttribute, NumberAttribute, UnicodeAttribute
from pynamodb.indexes import AllProjection, GlobalSecondaryIndex

from .base import DynamoMeta, DynamoModel, KeyAttribute


class GSI1Index(GlobalSecondaryIndex):
    class Meta(DynamoMeta):
        index_name = "gsi1"
        projection = AllProjection()

    gsi1pk = KeyAttribute(hash_key=True, prefix="EVENT#")
    gsi1sk = KeyAttribute(range_key=True, prefix="AT#")


class EventPersistence(DynamoModel, discriminator="EVENT"):
    # Keys
    pk = KeyAttribute(hash_key=True, default="EVENT")
    sk = KeyAttribute(range_key=True, prefix="EVENT#")
    # Index
    gsi1pk = KeyAttribute(prefix="ACCOUNT#")
    gsi1sk = KeyAttribute(prefix="AT#")
    gsi1 = GSI1Index()
    # Attributes
    id = KeyAttribute(null=False)
    account = UnicodeAttribute(null=False)
    region = UnicodeAttribute(null=True)
    source = UnicodeAttribute(null=False)
    detail = UnicodeAttribute(null=False)
    detail_type = UnicodeAttribute(null=True)
    resources = ListAttribute(null=True, default=lambda: [])
    assigned = UnicodeAttribute(null=True)
    status = NumberAttribute(null=True)
    published_at = NumberAttribute(null=False)
    expired_at = NumberAttribute(null=True)
    updated_at = NumberAttribute(null=False)
