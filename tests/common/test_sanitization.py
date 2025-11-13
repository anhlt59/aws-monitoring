"""Tests for sensitive data sanitization utilities"""

import pytest

from src.common.utils.sanitization import sanitize_dict, sanitize_log_entry, sanitize_logs, sanitize_text


class TestSanitizeText:
    """Test sanitize_text function"""

    def test_sanitize_aws_access_key(self):
        """Test sanitization of AWS access keys"""
        text = "Using access key AKIAIOSFODNN7EXAMPLE for authentication"
        sanitized = sanitize_text(text)
        assert "AKIAIOSFODNN7EXAMPLE" not in sanitized
        assert "[AWS_ACCESS_KEY]" in sanitized

    def test_sanitize_email(self):
        """Test sanitization of email addresses"""
        text = "Contact user@example.com for support"
        sanitized = sanitize_text(text)
        assert "user@example.com" not in sanitized
        assert "[EMAIL]" in sanitized

    def test_sanitize_ipv4(self):
        """Test sanitization of IPv4 addresses"""
        text = "Connection from 192.168.1.100 failed"
        sanitized = sanitize_text(text)
        assert "192.168.1.100" not in sanitized
        assert "[IP_ADDRESS]" in sanitized

    def test_sanitize_phone_number(self):
        """Test sanitization of phone numbers"""
        text = "Call support at +1-555-123-4567"
        sanitized = sanitize_text(text)
        assert "555-123-4567" not in sanitized
        assert "[PHONE]" in sanitized

    def test_sanitize_jwt_token(self):
        """Test sanitization of JWT tokens"""
        text = "Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
        sanitized = sanitize_text(text)
        assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in sanitized
        assert "[JWT_TOKEN]" in sanitized

    def test_sanitize_multiple_patterns(self):
        """Test sanitization of multiple sensitive patterns"""
        text = "User user@example.com connected from 192.168.1.100 with key AKIAIOSFODNN7EXAMPLE"
        sanitized = sanitize_text(text)
        assert "user@example.com" not in sanitized
        assert "192.168.1.100" not in sanitized
        assert "AKIAIOSFODNN7EXAMPLE" not in sanitized
        assert "[EMAIL]" in sanitized
        assert "[IP_ADDRESS]" in sanitized
        assert "[AWS_ACCESS_KEY]" in sanitized

    def test_empty_text(self):
        """Test with empty text"""
        assert sanitize_text("") == ""

    def test_text_without_sensitive_data(self):
        """Test text without sensitive data remains unchanged"""
        text = "Normal log message without sensitive data"
        sanitized = sanitize_text(text)
        assert sanitized == text


class TestSanitizeDict:
    """Test sanitize_dict function"""

    def test_sanitize_dict_values(self):
        """Test sanitization of dictionary string values"""
        data = {
            "message": "Error connecting to 192.168.1.100",
            "user": "test@example.com",
            "status": "failed",
        }
        sanitized = sanitize_dict(data)
        assert "192.168.1.100" not in sanitized["message"]
        assert "[IP_ADDRESS]" in sanitized["message"]
        assert "test@example.com" not in sanitized["user"]
        assert "[EMAIL]" in sanitized["user"]
        assert sanitized["status"] == "failed"

    def test_sanitize_nested_dict(self):
        """Test sanitization of nested dictionaries"""
        data = {
            "user": {
                "email": "user@example.com",
                "ip": "192.168.1.100",
            },
            "metadata": {"status": "active"},
        }
        sanitized = sanitize_dict(data)
        assert "user@example.com" not in sanitized["user"]["email"]
        assert "192.168.1.100" not in sanitized["user"]["ip"]

    def test_sanitize_dict_with_lists(self):
        """Test sanitization of dictionaries containing lists"""
        data = {
            "errors": [
                {"message": "Connection from 192.168.1.100 failed"},
                {"message": "Auth failed for user@example.com"},
            ]
        }
        sanitized = sanitize_dict(data)
        assert "192.168.1.100" not in str(sanitized)
        assert "user@example.com" not in str(sanitized)

    def test_non_dict_input(self):
        """Test with non-dict input"""
        result = sanitize_dict("not a dict")
        assert result == "not a dict"


class TestSanitizeLogEntry:
    """Test sanitize_log_entry function"""

    def test_sanitize_string_log(self):
        """Test sanitizing a string log entry"""
        log = "Error: Connection from 192.168.1.100 failed"
        sanitized = sanitize_log_entry(log)
        assert "192.168.1.100" not in sanitized
        assert "[IP_ADDRESS]" in sanitized

    def test_sanitize_dict_log(self):
        """Test sanitizing a dictionary log entry"""
        log = {"message": "Error from user@example.com", "level": "ERROR"}
        sanitized = sanitize_log_entry(log)
        assert "user@example.com" not in sanitized["message"]
        assert "[EMAIL]" in sanitized["message"]


class TestSanitizeLogs:
    """Test sanitize_logs function"""

    def test_sanitize_list_of_strings(self):
        """Test sanitizing a list of string logs"""
        logs = [
            "Error from 192.168.1.100",
            "User user@example.com logged in",
            "Normal log message",
        ]
        sanitized = sanitize_logs(logs)
        assert len(sanitized) == 3
        assert "192.168.1.100" not in sanitized[0]
        assert "user@example.com" not in sanitized[1]
        assert sanitized[2] == "Normal log message"

    def test_sanitize_list_of_dicts(self):
        """Test sanitizing a list of dictionary logs"""
        logs = [
            {"message": "Error from 192.168.1.100"},
            {"message": "User user@example.com logged in"},
        ]
        sanitized = sanitize_logs(logs)
        assert len(sanitized) == 2
        assert "192.168.1.100" not in sanitized[0]["message"]
        assert "user@example.com" not in sanitized[1]["message"]

    def test_empty_list(self):
        """Test with empty list"""
        assert sanitize_logs([]) == []
