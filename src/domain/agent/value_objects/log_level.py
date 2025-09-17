from enum import Enum


class LogLevel(Enum):
    """Log level for agent monitoring"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

    def is_error_level(self) -> bool:
        """Check if log level indicates an error"""
        return self in [self.ERROR, self.CRITICAL]

    def get_severity_weight(self) -> int:
        """Get numeric weight for severity comparison"""
        weights = {self.DEBUG: 1, self.INFO: 2, self.WARNING: 3, self.ERROR: 4, self.CRITICAL: 5}
        return weights[self]
