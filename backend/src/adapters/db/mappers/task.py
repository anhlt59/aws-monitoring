import json

from src.adapters.db.models import TaskPersistence
from src.adapters.db.models.task import AssignedUserPersistence, CommentPersistence
from src.domain.models import AssignedUser, Task, TaskComment


class TaskMapper:
    @classmethod
    def to_persistence(cls, model: Task) -> TaskPersistence:
        # Convert AssignedUser to AssignedUserPersistence
        assigned_user_persistence = AssignedUserPersistence(
            id=model.assigned_user.id,
            name=model.assigned_user.name,
        )

        # Convert TaskComment list to CommentPersistence list
        comments_persistence = [
            CommentPersistence(
                id=comment.id,
                user_id=comment.user_id,
                user_name=comment.user_name,
                comment=comment.comment,
                created_at=comment.created_at,
            )
            for comment in model.comments
        ]

        return TaskPersistence(
            # Keys
            pk="TASK",
            sk=model.persistence_id,
            # Attributes
            id=model.id,
            title=model.title,
            description=model.description,
            status=model.status.value,
            priority=model.priority.value,
            assigned_user=assigned_user_persistence,
            event_id=model.event_id,
            event_details=json.dumps(model.event_details) if model.event_details else None,
            due_date=model.due_date,
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            closed_at=model.closed_at,
            comments=comments_persistence,
            # GSI1 keys
            gsi1pk=model.assigned_user.id,
            gsi1sk=f"{model.status.value}#{model.priority.value}#{model.id}",
            # GSI2 keys
            gsi2pk=model.status.value,
            gsi2sk=f"{model.created_at}#{model.id}",
        )

    @classmethod
    def to_entity(cls, persistence: TaskPersistence) -> Task:
        # Convert AssignedUserPersistence to AssignedUser
        assigned_user = AssignedUser(
            id=persistence.assigned_user.id,
            name=persistence.assigned_user.name,
        )

        # Convert CommentPersistence list to TaskComment list
        comments = [
            TaskComment(
                id=comment.id,
                user_id=comment.user_id,
                user_name=comment.user_name,
                comment=comment.comment,
                created_at=comment.created_at,
            )
            for comment in persistence.comments
        ]

        return Task(
            id=persistence.id,
            title=persistence.title,
            description=persistence.description,
            status=persistence.status,
            priority=persistence.priority,
            assigned_user=assigned_user,
            event_id=persistence.event_id,
            event_details=json.loads(persistence.event_details) if persistence.event_details else None,
            due_date=persistence.due_date,
            created_at=persistence.created_at,
            updated_at=persistence.updated_at,
            created_by=persistence.created_by,
            closed_at=persistence.closed_at,
            comments=comments,
        )
