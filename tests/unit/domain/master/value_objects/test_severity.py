from src.domain.master.value_objects.severity import Severity


class TestSeverity:
    """Test cases for Severity value object"""

    def test_severity_values(self):
        """Test severity enum values"""
        assert Severity.UNKNOWN.value == 0
        assert Severity.LOW.value == 1
        assert Severity.MEDIUM.value == 2
        assert Severity.HIGH.value == 3
        assert Severity.CRITICAL.value == 4

    def test_severity_ordering(self):
        """Test severity ordering (IntEnum behavior)"""
        assert Severity.UNKNOWN < Severity.LOW
        assert Severity.LOW < Severity.MEDIUM
        assert Severity.MEDIUM < Severity.HIGH
        assert Severity.HIGH < Severity.CRITICAL

        # Test comparison with integers
        assert Severity.HIGH >= 3
        assert Severity.CRITICAL > Severity.HIGH

    def test_from_string_method(self):
        """Test from_string class method"""
        assert Severity.from_string("critical") == Severity.CRITICAL
        assert Severity.from_string("CRITICAL") == Severity.CRITICAL
        assert Severity.from_string("high") == Severity.HIGH
        assert Severity.from_string("medium") == Severity.MEDIUM
        assert Severity.from_string("low") == Severity.LOW
        assert Severity.from_string("unknown") == Severity.UNKNOWN

        # Invalid string should return UNKNOWN
        assert Severity.from_string("invalid") == Severity.UNKNOWN
        assert Severity.from_string("") == Severity.UNKNOWN

    def test_is_critical_method(self):
        """Test is_critical method"""
        assert Severity.CRITICAL.is_critical() is True
        assert Severity.HIGH.is_critical() is True
        assert Severity.MEDIUM.is_critical() is False
        assert Severity.LOW.is_critical() is False
        assert Severity.UNKNOWN.is_critical() is False

    def test_requires_immediate_action_method(self):
        """Test requires_immediate_action method"""
        assert Severity.CRITICAL.requires_immediate_action() is True
        assert Severity.HIGH.requires_immediate_action() is False
        assert Severity.MEDIUM.requires_immediate_action() is False
        assert Severity.LOW.requires_immediate_action() is False
        assert Severity.UNKNOWN.requires_immediate_action() is False
