"""Application constants for mon."""

from pathlib import Path

# Application metadata
APP_NAME = "mon"
APP_VERSION = "1.0.0"

# File extensions
YAML_EXTENSIONS = [".yml", ".yaml"]

# Default directories
DEFAULT_CONFIG_DIR = Path("backend/infra/configs")
# Legacy paths (kept for backward compatibility)
AGENT_CONFIG_DIR = Path("backend/infra/configs")  # Now unified with master configs

# UI Constants
MAX_DISPLAY_ITEMS = 20
EDITOR_SAVE_KEY = "ctrl+s"
EDITOR_EXIT_KEY = "esc"
