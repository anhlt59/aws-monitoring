from pynamodb.attributes import NumberAttribute, UnicodeAttribute

from src.common.utils.datetime_utils import current_utc_timestamp
from src.infras.db.model import DynamoModel, KeyAttribute


class AgentPersistence(DynamoModel, discriminator="AGENT"):
    # Keys
    pk = KeyAttribute(hash_key=True, default="AGENT")
    sk = KeyAttribute(range_key=True, prefix="AGENT#")
    # Attributes
    region = UnicodeAttribute(null=False)
    status = UnicodeAttribute(null=True)
    deployed_at = NumberAttribute(null=False)
    created_at = NumberAttribute(default_for_new=current_utc_timestamp)
