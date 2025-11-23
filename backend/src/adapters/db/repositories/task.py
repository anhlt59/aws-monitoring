from src.adapters.db.mappers import TaskMapper
from src.adapters.db.models import TaskPersistence
from src.adapters.db.repositories.base import DynamoRepository
from src.domain.models import Task, TaskPriority, TaskStatus


class TaskRepository(DynamoRepository):
    model_cls = TaskPersistence
    mapper = TaskMapper

    def get(self, task_id: str) -> Task:
        """Get task by ID (includes all comments)."""
        model = self._get(hash_key="TASK", range_key=f"TASK#{task_id}")
        return self.mapper.to_entity(model)

    def list_all(self) -> list[Task]:
        """List all tasks, sorted by ID."""
        result = self._query(hash_key="TASK")
        return [self.mapper.to_entity(item) for item in result]

    def list_by_assigned_user(self, user_id: str) -> list[Task]:
        """Get tasks assigned to a user, sorted by status & priority."""
        result = self._query(
            hash_key=f"ASSIGNED#{user_id}",
            index=self.model_cls.gsi1,
        )
        return [self.mapper.to_entity(item) for item in result]

    def list_by_assigned_user_and_status(self, user_id: str, status: TaskStatus) -> list[Task]:
        """Get tasks assigned to a user filtered by status."""
        range_key_condition = self.model_cls.gsi1sk.begins_with(f"STATUS#{status.value}#")
        result = self._query(
            hash_key=f"ASSIGNED#{user_id}",
            range_key_condition=range_key_condition,
            index=self.model_cls.gsi1,
        )
        return [self.mapper.to_entity(item) for item in result]

    def list_by_status(self, status: TaskStatus) -> list[Task]:
        """List tasks by status, sorted by creation time."""
        result = self._query(
            hash_key=f"STATUS#{status.value}",
            index=self.model_cls.gsi2,
        )
        return [self.mapper.to_entity(item) for item in result]

    def list_by_status_and_date_range(
        self, status: TaskStatus, start_date: int | None = None, end_date: int | None = None
    ) -> list[Task]:
        """List tasks by status and date range."""
        if start_date and end_date:
            range_key_condition = self.model_cls.gsi2sk.between(
                f"CREATED#{start_date}", f"CREATED#{end_date}"
            )
        elif start_date:
            range_key_condition = self.model_cls.gsi2sk >= f"CREATED#{start_date}"
        elif end_date:
            range_key_condition = self.model_cls.gsi2sk <= f"CREATED#{end_date}"
        else:
            range_key_condition = None

        result = self._query(
            hash_key=f"STATUS#{status.value}",
            range_key_condition=range_key_condition,
            index=self.model_cls.gsi2,
        )
        return [self.mapper.to_entity(item) for item in result]

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
