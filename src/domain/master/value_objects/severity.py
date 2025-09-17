from enum import IntEnum


class Severity(IntEnum):
    """Severity levels for monitoring events"""

    UNKNOWN = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

    @classmethod
    def from_string(cls, value: str) -> "Severity":
        """Create Severity from string representation"""
        mapping = {
            "unknown": cls.UNKNOWN,
            "low": cls.LOW,
            "medium": cls.MEDIUM,
            "high": cls.HIGH,
            "critical": cls.CRITICAL,
        }
        return mapping.get(value.lower(), cls.UNKNOWN)

    def is_critical(self) -> bool:
        """Check if severity is critical or high"""
        return self >= self.HIGH

    def requires_immediate_action(self) -> bool:
        """Check if severity requires immediate action"""
        return self == self.CRITICAL
