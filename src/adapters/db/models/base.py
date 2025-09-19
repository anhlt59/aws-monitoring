from typing import Any

from pynamodb.attributes import DiscriminatorAttribute, UnicodeAttribute
from pynamodb.models import Model

from src.common.constants import AWS_DYNAMODB_TABLE, AWS_ENDPOINT, AWS_REGION


# Attributes -----------------------------------------------------------
class KeyAttribute(UnicodeAttribute):
    prefix: str | None

    def __init__(self, prefix: str | None = None, **kwargs):
        super().__init__(**kwargs)
        self.prefix = prefix

    def serialize(self, value: str) -> str:
        if self.prefix is not None:
            value = f"{self.prefix}{value}"
        return super().serialize(value)

    def deserialize(self, value: str) -> str:
        if "#" in value:
            value = value.rsplit("#", 1)[-1]
        return super().deserialize(value)

    def __set__(self, instance: Any, value: Any) -> None:
        if isinstance(value, str) and self.prefix and value.startswith(self.prefix):
            value = value.strip(self.prefix)
        return super().__set__(instance, value)


# Model --------------------------------------------------------------
class DynamoMeta:
    table_name: str = AWS_DYNAMODB_TABLE
    host: str | None = AWS_ENDPOINT
    region: str | None = AWS_REGION


class DynamoModel(Model):
    Meta = DynamoMeta
    # Keys
    pk = UnicodeAttribute(hash_key=True)
    sk = UnicodeAttribute(range_key=True)
    # Attributes
    type = DiscriminatorAttribute()
