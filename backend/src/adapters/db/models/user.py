from pynamodb.attributes import BooleanAttribute, NumberAttribute, UnicodeAttribute

from .base import DynamoModel, KeyAttribute


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
    is_active = BooleanAttribute(null=False, default=True)
    created_at = NumberAttribute(null=False)
    updated_at = NumberAttribute(null=False)
    last_login = NumberAttribute(null=True)
    # GSI1 keys for querying by email
    gsi1pk = KeyAttribute(hash_key=True, default="EMAIL")
    gsi1sk = UnicodeAttribute(null=True)  # EMAIL#{email}
    # GSI2 keys for querying by role
    gsi2pk = UnicodeAttribute(null=True)  # ROLE#{role}
    gsi2sk = UnicodeAttribute(null=True)  # USER#{user_id}
