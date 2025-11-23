"""List users use case."""

from pydantic import Field

from src.adapters.db.repositories.user import UserRepository
from src.common.models import BaseModel
from src.domain.models.user import UserProfile, UserRole


class ListUsersDTO(BaseModel):
    """Data transfer object for listing users."""

    role: UserRole | None = Field(None, description="Filter by role")
    search: str | None = Field(None, description="Search by email")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")


class PaginatedUsersDTO(BaseModel):
    """Paginated users response."""

    items: list[UserProfile]
    total: int
    page: int
    page_size: int
    has_more: bool


class ListUsers:
    """
    Use case for listing users with filters and pagination.

    Supports filtering by role and email search.
    Requires admin permissions.
    """

    def __init__(self, user_repository: UserRepository | None = None):
        """
        Initialize use case.

        Args:
            user_repository: User repository instance
        """
        self.user_repository = user_repository or UserRepository()

    def execute(self, dto: ListUsersDTO) -> PaginatedUsersDTO:
        """
        List users with filters.

        Args:
            dto: Filter and pagination parameters

        Returns:
            Paginated users response
        """
        # Use repository methods based on filters
        if dto.role:
            users = self.user_repository.list_by_role(dto.role)
        else:
            users = self.user_repository.list_all()

        # Apply search filter
        if dto.search:
            search_term = dto.search.lower()
            users = [u for u in users if search_term in u.email.lower() or search_term in u.full_name.lower()]

        # Convert to profiles
        profiles = [UserProfile.from_user(u) for u in users]

        # Calculate pagination
        total = len(profiles)
        start_idx = (dto.page - 1) * dto.page_size
        end_idx = start_idx + dto.page_size
        paginated_profiles = profiles[start_idx:end_idx]
        has_more = end_idx < total

        return PaginatedUsersDTO(
            items=paginated_profiles,
            total=total,
            page=dto.page,
            page_size=dto.page_size,
            has_more=has_more,
        )
