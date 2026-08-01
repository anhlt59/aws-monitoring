from pynamodb.attributes import NumberAttribute, UnicodeAttribute
from pynamodb.indexes import AllProjection, GlobalSecondaryIndex

from .base import DynamoMeta, DynamoModel, KeyAttribute


class GSI1Index(GlobalSecondaryIndex):
    class Meta(DynamoMeta):
        index_name = "gsi1"
        projection = AllProjection()

    gsi1pk = KeyAttribute(hash_key=True, default="EMAIL")
    gsi1sk = KeyAttribute(range_key=True, prefix="EVENT#")


class GSI2Index(GlobalSecondaryIndex):
    class Meta(DynamoMeta):
        index_name = "gsi2"
        projection = AllProjection()

    gsi1pk = KeyAttribute(hash_key=True, prefix="SOURCE#")
    gsi1sk = KeyAttribute(range_key=True, prefix="EVENT#")


class UserPersistence(DynamoModel, discriminator="USER"):
    # Keys
    pk = KeyAttribute(hash_key=True, default="USER")
    sk = KeyAttribute(range_key=True, prefix="USER#")  # USER#{user_id}
    # Attributes
    id = UnicodeAttribute(null=False)
    email = UnicodeAttribute(null=False)
    full_name = UnicodeAttribute(null=False)
    password_hash = UnicodeAttribute(null=False)
    role = UnicodeAttribute(null=False)  # admin, user
    created_at = NumberAttribute(null=False)
    updated_at = NumberAttribute(null=False)
    # GSI1 keys for querying by email
    gsi1 = GSI1Index()
    gsi1pk = KeyAttribute(default="EMAIL")
    gsi1sk = KeyAttribute(prefix="EMAIL#")  # EMAIL#{email}
    # GSI2 keys for querying by role
    gsi2 = GSI2Index()
    gsi2pk = KeyAttribute(prefix="ROLE#")  # ROLE#{role}
    gsi2sk = KeyAttribute(prefix="USER")  # USER#{user_id}
