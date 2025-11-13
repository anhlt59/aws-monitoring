"""Utility functions for monterm."""

from pathlib import Path
from typing import Any

import yaml


def flatten_dict(data: dict[str, Any], parent_key: str = "", separator: str = ".") -> dict[str, Any]:
    """
    Flatten a nested dictionary into a single-level dictionary with dotted keys.

    Args:
        data: The dictionary to flatten
        parent_key: The parent key prefix
        separator: The separator to use between keys

    Returns:
        Flattened dictionary with dotted keys
    """
    items: list[tuple[str, Any]] = []

    for key, value in data.items():
        new_key = f"{parent_key}{separator}{key}" if parent_key else key

        if isinstance(value, dict):
            items.extend(flatten_dict(value, new_key, separator).items())
        else:
            items.append((new_key, value))

    return dict(items)


def unflatten_dict(data: dict[str, Any], separator: str = ".") -> dict[str, Any]:
    """
    Unflatten a dictionary with dotted keys into a nested dictionary.

    Args:
        data: The flattened dictionary
        separator: The separator used between keys

    Returns:
        Nested dictionary
    """
    result: dict[str, Any] = {}

    for key, value in data.items():
        parts = key.split(separator)
        current = result

        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]

        current[parts[-1]] = value

    return result


def validate_yaml_structure(data: Any) -> bool:
    """
    Validate that the data structure is a valid YAML-compatible dictionary.

    Args:
        data: The data to validate

    Returns:
        True if valid, False otherwise
    """
    if not isinstance(data, dict):
        return False

    # Try to serialize and deserialize to ensure it's valid YAML
    try:
        yaml_str = yaml.dump(data, default_flow_style=False, sort_keys=False)
        yaml.safe_load(yaml_str)
        return True
    except (yaml.YAMLError, TypeError):
        return False


def format_yaml_value(value: Any) -> str:
    """
    Format a YAML value for display.

    Args:
        value: The value to format

    Returns:
        Formatted string representation
    """
    if isinstance(value, str):
        # Handle multi-line strings
        if "\n" in value:
            return "[Multi-line text]"
        return value
    elif isinstance(value, bool):
        return str(value).lower()
    elif value is None:
        return "null"
    elif isinstance(value, (list, dict)):
        return f"[{type(value).__name__}]"
    else:
        return str(value)
