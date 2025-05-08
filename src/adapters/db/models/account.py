from pynamodb.attributes import ListAttribute, UnicodeAttribute

from .base import DynamoModel, KeyAttribute


class AccountPersistence(DynamoModel, discriminator="ACCOUNT"):
    # Keys
    pk = KeyAttribute(hash_key=True, prefix="PROJECT#")
    sk = KeyAttribute(range_key=True, prefix="ACCOUNT#")
    # Attributes
    name = UnicodeAttribute(null=False)
    active_regions = ListAttribute(of=UnicodeAttribute, null=False)
    assume_role_arn = UnicodeAttribute(null=False)
