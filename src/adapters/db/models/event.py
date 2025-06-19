from pynamodb.attributes import NumberAttribute, UnicodeAttribute
from uuid_utils import uuid7

from .base import DynamoModel, KeyAttribute


class EventPersistence(DynamoModel, discriminator="EVENT"):
    # Keys
    pk = KeyAttribute(hash_key=True, default="EVENT")
    sk = KeyAttribute(range_key=True, prefix="EVENT#", default_for_new=lambda: str(uuid7()))
    # Attributes
    project = UnicodeAttribute(null=False)
    source = UnicodeAttribute(null=False)
    detail = UnicodeAttribute(null=False)
    assigned = UnicodeAttribute(null=True)
    status = NumberAttribute(null=True)
