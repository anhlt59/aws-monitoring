from pynamodb.attributes import NumberAttribute, UnicodeAttribute

from .base import DynamoModel, KeyAttribute


class AwsConfigPersistence(DynamoModel, discriminator="CONFIG"):
    # Keys (Singleton: pk=CONFIG, sk=AWS)
    pk = KeyAttribute(hash_key=True, default="CONFIG")
    sk = KeyAttribute(range_key=True, default="AWS")
    # Attributes
    id = UnicodeAttribute(null=False)
    account_id = UnicodeAttribute(null=False)
    account_name = UnicodeAttribute(null=False)
    region = UnicodeAttribute(null=False)
    role_arn = UnicodeAttribute(null=True)
    status = UnicodeAttribute(null=False)  # pending, deploying, active, failed, disabled
    deployed_at = NumberAttribute(null=True)
    last_sync = NumberAttribute(null=True)
    created_at = NumberAttribute(null=False)
    updated_at = NumberAttribute(null=False)
