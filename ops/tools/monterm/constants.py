"""Application constants for monterm."""

from pathlib import Path

# Application metadata
APP_NAME = "monterm"
APP_VERSION = "1.0.0"

# File extensions
YAML_EXTENSIONS = [".yml", ".yaml"]

# Default directories
DEFAULT_CONFIG_DIR = Path("infra/master/configs")
AGENT_CONFIG_DIR = Path("infra/agent/configs")

# UI Constants
MAX_DISPLAY_ITEMS = 20
EDITOR_SAVE_KEY = "ctrl+s"
EDITOR_EXIT_KEY = "esc"
