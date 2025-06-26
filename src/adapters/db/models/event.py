from pynamodb.attributes import NumberAttribute, UnicodeAttribute

from .base import DynamoModel, KeyAttribute


class EventPersistence(DynamoModel, discriminator="EVENT"):
    # Keys
    pk = KeyAttribute(hash_key=True, default="EVENT")
    sk = KeyAttribute(range_key=True, prefix="EVENT#")
    # Attributes
    account = UnicodeAttribute(null=False)
    source = UnicodeAttribute(null=False)
    detail = UnicodeAttribute(null=False)
    assigned = UnicodeAttribute(null=True)
    status = NumberAttribute(null=True)
    published_at = NumberAttribute(null=False)
    expired_at = NumberAttribute(null=True)
    updated_at = NumberAttribute(null=False)
