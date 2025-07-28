from pynamodb.attributes import NumberAttribute, UnicodeAttribute

from src.common.utils.datetime_utils import current_utc_timestamp

from .base import DynamoModel, KeyAttribute


class AccountPersistence(DynamoModel, discriminator="ACCOUNT"):
    # Keys
    pk = KeyAttribute(hash_key=True, default="ACCOUNT")
    sk = KeyAttribute(range_key=True, prefix="ACCOUNT#")
    # Attributes
    name = UnicodeAttribute(null=False)
    stage = UnicodeAttribute(null=True)
    region = UnicodeAttribute(null=False)
    deployed_at = NumberAttribute(null=False)
    created_at = NumberAttribute(default_for_new=current_utc_timestamp)
