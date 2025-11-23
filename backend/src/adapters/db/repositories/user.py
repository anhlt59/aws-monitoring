from src.adapters.db.mappers import UserMapper
from src.adapters.db.models import UserPersistence
from src.adapters.db.repositories.base import DynamoRepository
from src.domain.models import User, UserRole


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
            from src.common.exceptions import NotFoundError

            raise NotFoundError(f"User with email {email} not found")
        return self.mapper.to_entity(items[0])

    def list_all(self) -> list[User]:
        """List all users, ordered by created_at."""
        result = self._query(hash_key="USER")
        return [self.mapper.to_entity(item) for item in result]

    def list_by_role(self, role: UserRole) -> list[User]:
        """List users by role, ordered by created_at."""
        result = self._query(
            hash_key=f"ROLE#{role.value}",
            index=self.model_cls.gsi2,
        )
        return [self.mapper.to_entity(item) for item in result]

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
