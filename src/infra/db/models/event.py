from pynamodb.attributes import ListAttribute, NumberAttribute, UnicodeAttribute

from .base import DynamoModel, KeyAttribute


class EventPersistence(DynamoModel, discriminator="EVENT"):
    # Keys
    pk = KeyAttribute(hash_key=True, default="EVENT")
    sk = KeyAttribute(range_key=True, prefix="EVENT#")  # EVENT#{AWS EventTime}-{AWS EventID}
    # Attributes
    account = UnicodeAttribute(null=False)
    region = UnicodeAttribute(null=True)
    source = UnicodeAttribute(null=False)
    detail = UnicodeAttribute(null=False)
    detail_type = UnicodeAttribute(null=True)
    resources = ListAttribute(null=True, default=lambda: [])
    published_at = NumberAttribute(null=False)
    expired_at = NumberAttribute(null=True)
    updated_at = NumberAttribute(null=False)
