from enum import Enum


class AgentStatus(Enum):
    """Status values for monitoring agents"""

    CREATE_IN_PROGRESS = "CREATE_IN_PROGRESS"
    CREATE_COMPLETE = "CREATE_COMPLETE"
    CREATE_FAILED = "CREATE_FAILED"
    UPDATE_IN_PROGRESS = "UPDATE_IN_PROGRESS"
    UPDATE_COMPLETE = "UPDATE_COMPLETE"
    UPDATE_FAILED = "UPDATE_FAILED"
    DELETE_IN_PROGRESS = "DELETE_IN_PROGRESS"
    DELETE_COMPLETE = "DELETE_COMPLETE"
    DELETE_FAILED = "DELETE_FAILED"

    def is_healthy(self) -> bool:
        """Check if agent is in a healthy state"""
        return self in [self.CREATE_COMPLETE, self.UPDATE_COMPLETE]

    def is_in_progress(self) -> bool:
        """Check if agent is in a transitional state"""
        return self in [self.CREATE_IN_PROGRESS, self.UPDATE_IN_PROGRESS, self.DELETE_IN_PROGRESS]

    def is_failed(self) -> bool:
        """Check if agent is in a failed state"""
        return self in [self.CREATE_FAILED, self.UPDATE_FAILED, self.DELETE_FAILED]
