from src.adapters.db.models import UserPersistence
from src.domain.models import User


class UserMapper:
    @classmethod
    def to_persistence(cls, model: User) -> UserPersistence:
        return UserPersistence(
            # Keys
            pk="USER",
            sk=model.persistence_id,
            # Attributes
            id=model.id,
            email=model.email,
            full_name=model.full_name,
            password_hash=model.password_hash,
            role=model.role.value,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
            last_login=model.last_login,
            # GSI1 keys
            gsi1pk="EMAIL",
            gsi1sk=model.email,
            # GSI2 keys
            gsi2pk=f"ROLE#{model.role.value}",
            gsi2sk=f"USER#{model.id}",
        )

    @classmethod
    def to_entity(cls, persistence: UserPersistence) -> User:
        return User(
            id=persistence.id,
            email=persistence.email,
            full_name=persistence.full_name,
            password_hash=persistence.password_hash,
            role=persistence.role,
            is_active=persistence.is_active,
            created_at=persistence.created_at,
            updated_at=persistence.updated_at,
            last_login=persistence.last_login,
        )
