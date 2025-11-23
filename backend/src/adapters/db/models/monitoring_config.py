from pynamodb.attributes import NumberAttribute, UnicodeAttribute

from .base import DynamoModel, KeyAttribute


class MonitoringConfigPersistence(DynamoModel, discriminator="CONFIG"):
    # Keys (Singleton: pk=CONFIG, sk=MONITORING)
    pk = KeyAttribute(hash_key=True, default="CONFIG")
    sk = KeyAttribute(range_key=True, default="MONITORING")
    # Attributes
    services = UnicodeAttribute(null=False, default="[]")  # JSON array string
    global_settings = UnicodeAttribute(null=False, default="{}")  # JSON object string
    updated_at = NumberAttribute(null=False)
    updated_by = UnicodeAttribute(null=True)
