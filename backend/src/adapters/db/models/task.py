from pynamodb.attributes import ListAttribute, MapAttribute, NumberAttribute, UnicodeAttribute
from pynamodb.indexes import AllProjection, GlobalSecondaryIndex

from .base import DynamoMeta, DynamoModel, KeyAttribute


class GSI1Index(GlobalSecondaryIndex):
    class Meta(DynamoMeta):
        index_name = "gsi1"
        projection = AllProjection()

    gsi1pk = KeyAttribute(hash_key=True, prefix="ASSIGNED#")  # ASSIGNED#{user_id}
    gsi1sk = KeyAttribute(range_key=True, prefix="AT#")  # STATUS#{status}#PRIORITY#{priority}#TASK#{task_id}


class GSI2Index(GlobalSecondaryIndex):
    class Meta(DynamoMeta):
        index_name = "gsi2"
        projection = AllProjection()

    gsi1pk = KeyAttribute(hash_key=True, prefix="STATUS#")
    gsi1sk = KeyAttribute(range_key=True, prefix="CREATED#")


class CommentPersistence(MapAttribute):
    id = UnicodeAttribute(null=False)
    user_id = NumberAttribute(null=False)
    user_name = UnicodeAttribute(null=False)
    comment = UnicodeAttribute(null=False)
    created_at = NumberAttribute(null=False)


class AssignedUserPersistence(MapAttribute):
    id = NumberAttribute(null=False)
    name = NumberAttribute(null=False)


class TaskPersistence(DynamoModel, discriminator="TASK"):
    # Keys
    pk = KeyAttribute(hash_key=True, default="TASK")
    sk = KeyAttribute(range_key=True, prefix="TASK#")  # TASK#{task_id}

    # Attributes
    id = UnicodeAttribute(null=False)
    title = UnicodeAttribute(null=False)
    description = UnicodeAttribute(null=False)
    status = UnicodeAttribute(null=False)  # open, in_progress, closed
    priority = UnicodeAttribute(null=False)  # critical, high, medium, low
    assigned_user = AssignedUserPersistence(default=dict)  # Map: {"id": str, "name": str}
    event_id = UnicodeAttribute(null=True)
    event_details = UnicodeAttribute(null=True)  # JSON string
    due_date = NumberAttribute(null=True)
    created_at = NumberAttribute(null=False)
    updated_at = NumberAttribute(null=False)
    created_by = UnicodeAttribute(null=False)
    closed_at = NumberAttribute(null=True)
    comments = ListAttribute(of=CommentPersistence, default=list)

    # Indexes
    gsi1 = GSI1Index()
    gsi2 = GSI2Index()

    # GSI1 keys for querying by assigned user
    gsi1pk = UnicodeAttribute(null=True)  # ASSIGNED#{user_id}
    gsi1sk = UnicodeAttribute(null=True)  # STATUS#{status}#PRIORITY#{priority}#TASK#{task_id}
    # GSI2 keys for querying by status
    gsi2pk = UnicodeAttribute(null=True)  # STATUS#{status}
    gsi2sk = UnicodeAttribute(null=True)  # CREATED#{created_at}#TASK#{task_id}
