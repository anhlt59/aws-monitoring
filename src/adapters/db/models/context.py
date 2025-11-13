from pynamodb.attributes import NumberAttribute, UnicodeAttribute

from .base import DynamoModel, KeyAttribute


class ContextPersistence(DynamoModel, discriminator="CONTEXT"):
    """
    Store system context information for AI to understand the system better.
    Examples: architecture diagrams, API schemas, database schemas, etc.
    """

    # Keys
    pk = KeyAttribute(hash_key=True, default="CONTEXT")
    sk = KeyAttribute(range_key=True, prefix="CONTEXT#")  # CONTEXT#{context_type}#{context_id}
    # Attributes
    context_type = UnicodeAttribute(
        null=False
    )  # backend/database/api/architecture/infrastructure/deployment/etc
    title = UnicodeAttribute(null=False)  # Human-readable title
    content = UnicodeAttribute(null=False)  # JSON string with detailed context information
    version = UnicodeAttribute(null=False, default="1.0")  # Version of context for tracking updates
    created_at = NumberAttribute(null=False)
    updated_at = NumberAttribute(null=False)
