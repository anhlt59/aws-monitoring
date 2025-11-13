"""Tests for text similarity utilities"""

import pytest

from src.common.utils.text_similarity import (
    calculate_similarity,
    deduplicate_texts,
    find_duplicates,
    is_duplicate,
)


class TestCalculateSimilarity:
    """Test calculate_similarity function"""

    def test_identical_texts(self):
        """Test that identical texts have 100% similarity"""
        text1 = "Error: Connection timeout"
        text2 = "Error: Connection timeout"
        assert calculate_similarity(text1, text2) == 1.0

    def test_completely_different_texts(self):
        """Test that completely different texts have low similarity"""
        text1 = "Error: Connection timeout"
        text2 = "Success: Operation completed"
        similarity = calculate_similarity(text1, text2)
        assert similarity < 0.5

    def test_similar_texts(self):
        """Test that similar texts have high similarity"""
        text1 = "Error: Database connection timeout at 10:30:45"
        text2 = "Error: Database connection timeout at 10:30:46"
        similarity = calculate_similarity(text1, text2)
        assert similarity > 0.85

    def test_empty_texts(self):
        """Test handling of empty texts"""
        assert calculate_similarity("", "") == 0.0
        assert calculate_similarity("text", "") == 0.0
        assert calculate_similarity("", "text") == 0.0

    def test_whitespace_normalization(self):
        """Test that extra whitespace is normalized"""
        text1 = "Error:    Connection   timeout"
        text2 = "Error: Connection timeout"
        assert calculate_similarity(text1, text2) == 1.0


class TestIsDuplicate:
    """Test is_duplicate function"""

    def test_duplicate_detection_default_threshold(self):
        """Test duplicate detection with default threshold (85%)"""
        text1 = "Error: Connection failed at timestamp 123456"
        text2 = "Error: Connection failed at timestamp 123457"
        assert is_duplicate(text1, text2)

    def test_not_duplicate_default_threshold(self):
        """Test non-duplicate detection with default threshold"""
        text1 = "Error: Connection failed"
        text2 = "Error: Authentication failed"
        assert not is_duplicate(text1, text2)

    def test_custom_threshold(self):
        """Test duplicate detection with custom threshold"""
        text1 = "Error: Connection timeout"
        text2 = "Error: Connection failed"
        # These are similar but not 85% similar
        assert not is_duplicate(text1, text2, threshold=0.85)
        # But they might be 70% similar
        assert is_duplicate(text1, text2, threshold=0.50)


class TestFindDuplicates:
    """Test find_duplicates function"""

    def test_no_duplicates(self):
        """Test when there are no duplicates"""
        texts = [
            "Error: Connection timeout",
            "Error: Authentication failed",
            "Success: Operation completed",
        ]
        duplicates = find_duplicates(texts)
        assert duplicates == {}

    def test_with_duplicates(self):
        """Test when there are duplicates"""
        texts = [
            "Error: Connection timeout at 10:30:45",
            "Success: Operation completed",
            "Error: Connection timeout at 10:30:46",
            "Error: Connection timeout at 10:30:47",
        ]
        duplicates = find_duplicates(texts)
        # Index 0 should have duplicates at indices 2 and 3
        assert 0 in duplicates
        assert 2 in duplicates[0]
        assert 3 in duplicates[0]

    def test_empty_list(self):
        """Test with empty list"""
        assert find_duplicates([]) == {}


class TestDeduplicateTexts:
    """Test deduplicate_texts function"""

    def test_deduplicate_similar_logs(self):
        """Test deduplication of similar log entries"""
        texts = [
            "Error: Connection timeout at 10:30:45",
            "Error: Connection timeout at 10:30:46",
            "Error: Connection timeout at 10:30:47",
            "Success: Operation completed",
        ]
        unique = deduplicate_texts(texts)
        assert len(unique) == 2
        assert "Error: Connection timeout at 10:30:45" in unique
        assert "Success: Operation completed" in unique

    def test_deduplicate_keeps_first_occurrence(self):
        """Test that deduplication keeps the first occurrence"""
        texts = [
            "First occurrence",
            "First occurrence",
            "First occurrence",
        ]
        unique = deduplicate_texts(texts)
        assert len(unique) == 1
        assert unique[0] == "First occurrence"

    def test_empty_list(self):
        """Test with empty list"""
        assert deduplicate_texts([]) == []

    def test_single_item(self):
        """Test with single item"""
        texts = ["Single error message"]
        unique = deduplicate_texts(texts)
        assert len(unique) == 1
        assert unique[0] == "Single error message"

    def test_custom_threshold(self):
        """Test deduplication with custom threshold"""
        texts = [
            "Error: Connection timeout",
            "Error: Connection failed",
            "Error: Authentication failed",
        ]
        # With high threshold (85%), these should all be unique
        unique_high = deduplicate_texts(texts, threshold=0.85)
        assert len(unique_high) == 3

        # With lower threshold (50%), some might be considered duplicates
        unique_low = deduplicate_texts(texts, threshold=0.50)
        assert len(unique_low) <= 3
