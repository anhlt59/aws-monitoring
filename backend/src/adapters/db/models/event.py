from pynamodb.attributes import NumberAttribute, UnicodeAttribute
from pynamodb.indexes import AllProjection, GlobalSecondaryIndex

from .base import DynamoMeta, DynamoModel, KeyAttribute


class GSI1Index(GlobalSecondaryIndex):
    class Meta(DynamoMeta):
        index_name = "gsi1"
        projection = AllProjection()

    gsi1pk = KeyAttribute(hash_key=True, prefix="SOURCE#")
    gsi1sk = KeyAttribute(range_key=True, prefix="EVENT#")


class EventPersistence(DynamoModel, discriminator="EVENT"):
    # Keys
    pk = KeyAttribute(hash_key=True, default="EVENT")
    sk = KeyAttribute(range_key=True, prefix="EVENT#")  # EVENT#{id}
    # Attributes
    id = UnicodeAttribute(null=False)  # {published_at}-{event_id}
    account = UnicodeAttribute(null=False)
    region = UnicodeAttribute(null=False)
    source = UnicodeAttribute(null=False)
    detail_type = UnicodeAttribute(null=False)
    detail = UnicodeAttribute(null=False)  # JSON string
    severity = NumberAttribute(null=False, default=0)  # 0-5
    resources = UnicodeAttribute(null=False, default="[]")  # JSON array string
    published_at = NumberAttribute(null=False)
    updated_at = NumberAttribute(null=False)
    expired_at = NumberAttribute(null=False)  # TTL attribute

    # Indexes
    gsi1 = GSI1Index()
    # GSI1 index for querying by source
    gsi1pk = KeyAttribute(prefix="SOURCE#", null=False)  # SOURCE#{source}
    gsi1sk = KeyAttribute(prefix="EVENT#", null=False)  # EVENT#{id}
