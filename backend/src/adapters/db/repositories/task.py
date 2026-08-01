from common.utils.encoding import base64_to_json
from src.adapters.db.mappers import TaskMapper
from src.adapters.db.models import TaskPersistence
from src.domain.models import Task, TaskStatus
from .base import DynamoRepository, QueryResult

TaskQueryResult = QueryResult[Task]


class TaskRepository(DynamoRepository):
    model_cls = TaskPersistence
    mapper = TaskMapper

    def get(self, task_id: str) -> Task:
        """Get task by ID (includes all comments)."""
        model = self._get(hash_key="TASK", range_key=f"TASK#{task_id}")
        return self.mapper.to_entity(model)

    def all(self,
            direction: str = "desc",
            limit: int = 50,
            cursor: str | None = None,
            ) -> TaskQueryResult:
        """List all tasks, sorted by ID."""
        last_evaluated_key = base64_to_json(cursor) if cursor else None
        scan_index_forward = "asc" == direction

        result = self._query(
            hash_key="TASK",
            last_evaluated_key=last_evaluated_key,
            scan_index_forward=scan_index_forward,
            limit=limit,
        )

        return TaskQueryResult(
            items=[self.mapper.to_entity(item) for item in result],
            limit=limit,
            cursor=result.last_evaluated_key,
        )

    def list_by_assigned_user(
        self, user_id: str,
        status: TaskStatus | None = None,
        direction: str = "desc",
        limit: int = 50,
        cursor: str | None = None
    ) -> TaskQueryResult:
        """Get tasks assigned to a user, sorted by status & priority."""
        range_key_condition = self.model_cls.gsi1sk.begins_with(f"STATUS#{status.value}#") if status else None
        last_evaluated_key = base64_to_json(cursor) if cursor else None
        scan_index_forward = "asc" == direction

        result = self._query(
            hash_key=f"ASSIGNED#{user_id}",
            range_key_condition=range_key_condition,
            index=self.model_cls.gsi1,
            last_evaluated_key=last_evaluated_key,
            scan_index_forward=scan_index_forward,
            limit=limit,
        )
        return TaskQueryResult(
            items=[self.mapper.to_entity(item) for item in result],
            limit=limit,
            cursor=result.last_evaluated_key,
        )

    def list_by_status(self, status: TaskStatus, direction: str = "desc",
                       limit: int = 50,
                       cursor: str | None = None) -> TaskQueryResult:
        """List tasks by status, sorted by creation time."""
        last_evaluated_key = base64_to_json(cursor) if cursor else None
        scan_index_forward = "asc" == direction
        result = self._query(
            hash_key=f"STATUS#{status.value}",
            index=self.model_cls.gsi2,
            last_evaluated_key=last_evaluated_key,
            scan_index_forward=scan_index_forward,
            limit=limit,
        )
        return TaskQueryResult(
            items=[self.mapper.to_entity(item) for item in result],
            limit=limit,
            cursor=result.last_evaluated_key,
        )

    def create(self, entity: Task):
        """Create a new task."""
        model = self.mapper.to_persistence(entity)
        self._create(model)

    def update(self, entity: Task):
        """Update an existing task."""
        model = self.mapper.to_persistence(entity)
        model.save()

    def delete(self, task_id: str):
        """Delete a task by ID."""
        self._delete(hash_key="TASK", range_key=f"TASK#{task_id}")
