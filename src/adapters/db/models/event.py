from pynamodb.attributes import UnicodeAttribute

from .base import DynamoModel, KeyAttribute


class EventPersistence(DynamoModel, discriminator="EVENT"):
    # Keys
    pk = KeyAttribute(hash_key=True, prefix="PROJECT#")
    sk = KeyAttribute(range_key=True, prefix="ACCOUNT#")
    # Attributes
    name = UnicodeAttribute(null=False)
