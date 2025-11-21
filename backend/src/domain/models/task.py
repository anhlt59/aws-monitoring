"""Task domain models and related enums."""

from enum import Enum

from pydantic import Field, field_validator, model_validator
from pydantic_core import ValidationInfo

from src.common.models import BaseModel
from src.common.utils.datetime_utils import current_utc_timestamp


class TaskStatus(str, Enum):
    """Task status enumeration."""

    OPEN = "open"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"


class TaskPriority(str, Enum):
    """Task priority enumeration."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Task(BaseModel):
    """
    Task domain model.

    Represents a task created from monitoring events or manually created
    by users for tracking and resolution.
    """

    # Identity
    id: str  # Task UUID
    title: str
    description: str

    # Status & Priority
    status: TaskStatus = TaskStatus.OPEN
    priority: TaskPriority

    # Assignment
    assigned_user_id: str
    assigned_user_name: str | None = None  # Denormalized for display

    # Event Link (Optional)
    event_id: str | None = None  # Source event ID
    event_details: dict | None = None  # Denormalized event info
    # event_details structure:
    # {
    #   "account": "123456789012",
    #   "region": "us-east-1",
    #   "source": "aws.guardduty",
    #   "severity": "critical"
    # }

    # Scheduling
    due_date: int | None = None  # Unix timestamp (optional)

    # Timestamps
    created_at: int = Field(default_factory=current_utc_timestamp)
    updated_at: int = Field(default_factory=current_utc_timestamp)
    created_by: str  # User ID who created
    closed_at: int | None = None  # When task was closed

    # Denormalized counts
    comment_count: int = 0  # Number of comments

    @property
    def persistence_id(self) -> str:
        """DynamoDB sort key for task."""
        return self.id

    @property
    def is_open(self) -> bool:
        """Check if task is open."""
        return self.status == TaskStatus.OPEN

    @property
    def is_closed(self) -> bool:
        """Check if task is closed."""
        return self.status == TaskStatus.CLOSED

    @property
    def is_overdue(self) -> bool:
        """Check if task is overdue."""
        if self.due_date is None or self.is_closed:
            return False
        return current_utc_timestamp() > self.due_date

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        """Validate title is not empty."""
        value = value.strip()
        if not value or len(value) < 3:
            raise ValueError("Title must be at least 3 characters")
        if len(value) > 200:
            raise ValueError("Title cannot exceed 200 characters")
        return value

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str) -> str:
        """Validate description is not empty."""
        value = value.strip()
        if not value or len(value) < 10:
            raise ValueError("Description must be at least 10 characters")
        if len(value) > 5000:
            raise ValueError("Description cannot exceed 5000 characters")
        return value

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, value: int | None, info: ValidationInfo) -> int | None:
        """Validate due date is in the future."""
        if value is None:
            return value

        created_at = info.data.get("created_at", current_utc_timestamp())
        if value < created_at:
            raise ValueError("Due date cannot be in the past")

        return value

    @model_validator(mode="after")
    def validate_model(self):
        """Cross-field validation."""
        # Set closed_at when status changes to closed
        if self.status == TaskStatus.CLOSED and self.closed_at is None:
            self.closed_at = current_utc_timestamp()

        return self

    def update_status(self, new_status: TaskStatus) -> None:
        """
        Update task status and set timestamps accordingly.

        Args:
            new_status: The new status to set
        """
        old_status = self.status
        self.status = new_status
        self.updated_at = current_utc_timestamp()

        # Set closed_at when transitioning to closed
        if new_status == TaskStatus.CLOSED and old_status != TaskStatus.CLOSED:
            self.closed_at = current_utc_timestamp()

        # Clear closed_at when reopening
        if new_status != TaskStatus.CLOSED and old_status == TaskStatus.CLOSED:
            self.closed_at = None

    def assign_to_user(self, user_id: str, user_name: str) -> None:
        """
        Assign task to a user.

        Args:
            user_id: User ID to assign
            user_name: User full name (denormalized)
        """
        self.assigned_user_id = user_id
        self.assigned_user_name = user_name
        self.updated_at = current_utc_timestamp()

    def increment_comment_count(self) -> None:
        """Increment comment count when a comment is added."""
        self.comment_count += 1
        self.updated_at = current_utc_timestamp()

    def link_to_event(self, event_id: str, event_details: dict) -> None:
        """
        Link task to a source event.

        Args:
            event_id: Event ID to link
            event_details: Event metadata (account, region, source, severity)
        """
        self.event_id = event_id
        self.event_details = event_details
        self.updated_at = current_utc_timestamp()


class TaskComment(BaseModel):
    """
    Task comment model.

    Represents a comment on a task for discussion and updates.
    """

    # Identity
    id: str  # Comment UUID
    task_id: str

    # Author
    user_id: str
    user_name: str  # Denormalized for display

    # Content
    comment: str

    # Timestamp
    created_at: int = Field(default_factory=current_utc_timestamp)

    @property
    def persistence_id(self) -> str:
        """DynamoDB sort key for comment (chronologically ordered)."""
        return f"{self.created_at}#{self.id}"

    @field_validator("comment")
    @classmethod
    def validate_comment(cls, value: str) -> str:
        """Validate comment is not empty."""
        value = value.strip()
        if not value or len(value) < 1:
            raise ValueError("Comment cannot be empty")
        if len(value) > 2000:
            raise ValueError("Comment cannot exceed 2000 characters")
        return value


class TaskStatusHistory(BaseModel):
    """
    Task status change history.

    Tracks when task status changes for audit purposes.
    """

    task_id: str
    previous_status: TaskStatus
    new_status: TaskStatus
    changed_by: str  # User ID
    changed_at: int = Field(default_factory=current_utc_timestamp)
    comment: str | None = None  # Optional reason for change

    @property
    def persistence_id(self) -> str:
        """DynamoDB sort key for history."""
        return f"{self.changed_at}#{self.task_id}"
