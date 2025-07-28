from pynamodb.attributes import NumberAttribute, UnicodeAttribute
from pynamodb.indexes import AllProjection, LocalSecondaryIndex
from uuid_utils import uuid7

from src.common.utils.datetime_utils import current_utc_timestamp

from .base import DynamoMeta, DynamoModel, KeyAttribute


class LSIIndex(LocalSecondaryIndex):
    class Meta(DynamoMeta):
        index_name = "lsi1"
        projection = AllProjection()

    pk = KeyAttribute(hash_key=True, default="PROJECT")
    lsi1sk = KeyAttribute(range_key=True, prefix="ACCOUNT#")


class ProjectPersistence(DynamoModel, discriminator="PROJECT"):
    # Keys
    pk = KeyAttribute(hash_key=True, default="PROJECT")
    sk = KeyAttribute(range_key=True, prefix="PROJECT#", default_for_new=lambda: str(uuid7()))
    # Index
    sku = KeyAttribute(prefix="ACCOUNT#")
    lsi = LSIIndex()
    # Attributes
    name = UnicodeAttribute(null=False)
    stage = UnicodeAttribute(null=True)
    account_id = UnicodeAttribute(null=False)
    status = NumberAttribute(null=True)
    deployed_at = NumberAttribute(null=False)
    created_at = NumberAttribute(default_for_new=current_utc_timestamp)
