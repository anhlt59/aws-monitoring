"""File handler adapter for reading and writing YAML files."""

from pathlib import Path
from typing import Any

import yaml

from ops.tools.monterm.constants import YAML_EXTENSIONS
from ops.tools.monterm.models.profile import ProfileData, ProfileMetadata


class YAMLFileHandler:
    """Handler for YAML file operations."""

    def __init__(self, config_dir: Path):
        """
        Initialize the YAML file handler.

        Args:
            config_dir: Directory containing YAML configuration files
        """
        self.config_dir = Path(config_dir)

    def list_profiles(self) -> list[ProfileMetadata]:
        """
        List all YAML profiles in the configuration directory.

        Returns:
            List of profile metadata

        Raises:
            FileNotFoundError: If the configuration directory does not exist
        """
        if not self.config_dir.exists():
            raise FileNotFoundError(f"Configuration directory not found: {self.config_dir}")

        profiles = []
        for ext in YAML_EXTENSIONS:
            for file_path in self.config_dir.glob(f"*{ext}"):
                if file_path.is_file():
                    profile_name = file_path.stem
                    profiles.append(
                        ProfileMetadata(
                            name=profile_name,
                            path=file_path,
                            exists=True,
                        )
                    )

        # Sort by name
        return sorted(profiles, key=lambda p: p.name)

    def read_profile(self, profile_name: str) -> ProfileData:
        """
        Read a YAML profile from disk.

        Args:
            profile_name: Name of the profile (without extension)

        Returns:
            ProfileData instance

        Raises:
            FileNotFoundError: If the profile file does not exist
            yaml.YAMLError: If the YAML file is invalid
        """
        profile_path = self._find_profile_path(profile_name)

        if not profile_path or not profile_path.exists():
            raise FileNotFoundError(f"Profile not found: {profile_name}")

        with open(profile_path, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)

        if not isinstance(data, dict):
            raise ValueError(f"Invalid YAML structure in {profile_name}: expected a dictionary")

        return ProfileData.from_yaml(data)

    def write_profile(self, profile_name: str, profile_data: ProfileData) -> None:
        """
        Write a YAML profile to disk.

        Args:
            profile_name: Name of the profile (without extension)
            profile_data: Profile data to write

        Raises:
            ValueError: If the profile data is invalid
        """
        from ops.tools.monterm.utils import validate_yaml_structure

        yaml_data = profile_data.to_yaml()

        if not validate_yaml_structure(yaml_data):
            raise ValueError("Invalid YAML structure")

        profile_path = self._find_profile_path(profile_name)

        if not profile_path:
            # Create new file with .yml extension
            profile_path = self.config_dir / f"{profile_name}.yml"

        # Ensure parent directory exists
        profile_path.parent.mkdir(parents=True, exist_ok=True)

        with open(profile_path, "w", encoding="utf-8") as file:
            yaml.dump(
                yaml_data,
                file,
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True,
            )

    def create_profile(self, profile_name: str, template_data: dict[str, Any] | None = None) -> ProfileData:
        """
        Create a new YAML profile.

        Args:
            profile_name: Name of the new profile
            template_data: Optional template data for the new profile

        Returns:
            New ProfileData instance

        Raises:
            FileExistsError: If the profile already exists
        """
        profile_path = self._find_profile_path(profile_name)

        if profile_path and profile_path.exists():
            raise FileExistsError(f"Profile already exists: {profile_name}")

        # Use template or default structure
        if template_data is None:
            template_data = {
                "Region": "us-east-1",
                "Profile": profile_name,
            }

        profile_data = ProfileData.from_yaml(template_data)
        self.write_profile(profile_name, profile_data)

        return profile_data

    def delete_profile(self, profile_name: str) -> None:
        """
        Delete a YAML profile from disk.

        Args:
            profile_name: Name of the profile to delete

        Raises:
            FileNotFoundError: If the profile does not exist
        """
        profile_path = self._find_profile_path(profile_name)

        if not profile_path or not profile_path.exists():
            raise FileNotFoundError(f"Profile not found: {profile_name}")

        profile_path.unlink()

    def _find_profile_path(self, profile_name: str) -> Path | None:
        """
        Find the path to a profile file by name.

        Args:
            profile_name: Name of the profile (without extension)

        Returns:
            Path to the profile file, or None if not found
        """
        for ext in YAML_EXTENSIONS:
            profile_path = self.config_dir / f"{profile_name}{ext}"
            if profile_path.exists():
                return profile_path

        return None
