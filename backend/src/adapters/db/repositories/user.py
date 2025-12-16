from src.adapters.db.mappers import UserMapper
from src.adapters.db.models import UserPersistence
from src.common.exceptions import NotFoundError
from src.common.utils.encoding import base64_to_json
from src.domain.iam.models import User, UserRole

from .base import DynamoRepository, QueryResult

UserQueryResult = QueryResult[User]


class UserRepository(DynamoRepository):
    model_cls = UserPersistence
    mapper = UserMapper

    def get(self, user_id: str) -> User:
        """Get user by ID."""
        model = self._get(hash_key="USER", range_key=f"USER#{user_id}")
        return self.mapper.to_entity(model)

    def get_by_email(self, email: str) -> User:
        """Get user by email (for authentication)."""
        result = self._query(
            hash_key="EMAIL",
            range_key_condition=self.model_cls.gsi1sk == email,
            index=self.model_cls.gsi1,
            limit=1,
        )
        items = list(result)
        if not items:
            raise NotFoundError(f"User with email {email} not found")
        return self.mapper.to_entity(items[0])

    def all(self, direction: str = "desc", limit: int = 50, cursor: str | None = None) -> UserQueryResult:
        """List all users, ordered by created_at."""
        last_evaluated_key = base64_to_json(cursor) if cursor else None
        scan_index_forward = "asc" == direction

        result = self._query(
            hash_key="USER",
            scan_index_forward=scan_index_forward,
            last_evaluated_key=last_evaluated_key,
            limit=limit,
        )

        return UserQueryResult(
            items=[self.mapper.to_entity(item) for item in result],
            limit=limit,
            cursor=result.last_evaluated_key,
        )

    def list_by_role(
        self, role: UserRole, direction: str = "desc", limit: int = 50, cursor: str | None = None
    ) -> UserQueryResult:
        """List users by role, ordered by created_at."""
        last_evaluated_key = base64_to_json(cursor) if cursor else None
        scan_index_forward = "asc" == direction

        result = self._query(
            hash_key=f"ROLE#{role.value}",
            index=self.model_cls.gsi2,
            scan_index_forward=scan_index_forward,
            last_evaluated_key=last_evaluated_key,
            limit=limit,
        )
        return UserQueryResult(
            items=[self.mapper.to_entity(item) for item in result],
            limit=limit,
            cursor=result.last_evaluated_key,
        )

    def create(self, entity: User):
        """Create a new user."""
        model = self.mapper.to_persistence(entity)
        self._create(model)

    def update(self, entity: User):
        """Update an existing user."""
        model = self.mapper.to_persistence(entity)
        model.save()

    def delete(self, user_id: str):
        """Delete a user by ID."""
        self._delete(hash_key="USER", range_key=f"USER#{user_id}")
