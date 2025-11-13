"""
Text similarity utilities for duplicate detection in log analysis.
Uses difflib for fast sequence matching without external dependencies.
"""

from difflib import SequenceMatcher


def calculate_similarity(text1: str, text2: str) -> float:
    """
    Calculate similarity ratio between two text strings.

    Args:
        text1: First text string
        text2: Second text string

    Returns:
        Similarity ratio between 0.0 and 1.0 (1.0 = identical)
    """
    if not text1 or not text2:
        return 0.0

    # Normalize whitespace
    text1_normalized = " ".join(text1.split())
    text2_normalized = " ".join(text2.split())

    # Calculate similarity using SequenceMatcher
    matcher = SequenceMatcher(None, text1_normalized, text2_normalized)
    return matcher.ratio()


def is_duplicate(text1: str, text2: str, threshold: float = 0.85) -> bool:
    """
    Check if two texts are duplicates based on similarity threshold.

    Args:
        text1: First text string
        text2: Second text string
        threshold: Similarity threshold (default: 0.85 = 85%)

    Returns:
        True if similarity >= threshold, False otherwise
    """
    similarity = calculate_similarity(text1, text2)
    return similarity >= threshold


def find_duplicates(texts: list[str], threshold: float = 0.85) -> dict[int, list[int]]:
    """
    Find duplicate texts in a list based on similarity threshold.

    Args:
        texts: List of text strings
        threshold: Similarity threshold (default: 0.85 = 85%)

    Returns:
        Dictionary mapping unique text indices to lists of duplicate indices
        Example: {0: [2, 5], 1: [3, 4]} means texts[0] has duplicates at indices 2 and 5
    """
    if not texts:
        return {}

    duplicates = {}
    processed = set()

    for i, text1 in enumerate(texts):
        if i in processed:
            continue

        similar_indices = []
        for j, text2 in enumerate(texts[i + 1 :], start=i + 1):
            if is_duplicate(text1, text2, threshold):
                similar_indices.append(j)
                processed.add(j)

        if similar_indices:
            duplicates[i] = similar_indices

    return duplicates


def deduplicate_texts(texts: list[str], threshold: float = 0.85) -> list[str]:
    """
    Remove duplicate texts from a list based on similarity threshold.

    Args:
        texts: List of text strings
        threshold: Similarity threshold (default: 0.85 = 85%)

    Returns:
        List of unique texts (keeps first occurrence)
    """
    if not texts:
        return []

    unique_texts = []
    for text in texts:
        # Check if this text is similar to any already in unique_texts
        is_dup = any(is_duplicate(text, unique_text, threshold) for unique_text in unique_texts)
        if not is_dup:
            unique_texts.append(text)

    return unique_texts
