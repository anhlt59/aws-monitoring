from pynamodb.attributes import ListAttribute, NumberAttribute, UnicodeAttribute
from pynamodb.indexes import AllProjection, LocalSecondaryIndex

from .base import DynamoMeta, DynamoModel, KeyAttribute


class LSIIndex(LocalSecondaryIndex):
    class Meta(DynamoMeta):
        index_name = "lsi1"
        projection = AllProjection()

    pk = KeyAttribute(hash_key=True, default="EVENT")
    lsi1sk = KeyAttribute(range_key=True, prefix="ACCOUNT#")


class EventPersistence(DynamoModel, discriminator="EVENT"):
    # Keys
    pk = KeyAttribute(hash_key=True, default="EVENT")
    sk = KeyAttribute(range_key=True, prefix="EVENT#")
    # Index
    lsi1sk = KeyAttribute(prefix="ACCOUNT#")
    lsi = LSIIndex()
    # Attributes
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
