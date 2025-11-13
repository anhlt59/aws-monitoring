"""Business logic service for managing profiles."""

from pathlib import Path
from typing import Any

from ops.tools.monterm.adapters.file_handler import YAMLFileHandler
from ops.tools.monterm.models.profile import ProfileData, ProfileField, ProfileMetadata
from ops.tools.monterm.utils import flatten_dict, format_yaml_value


class ProfileService:
    """Service for managing configuration profiles."""

    def __init__(self, config_dir: Path):
        """
        Initialize the profile service.

        Args:
            config_dir: Directory containing configuration files
        """
        self.file_handler = YAMLFileHandler(config_dir)
        self.config_dir = config_dir

    def list_profiles(self) -> list[ProfileMetadata]:
        """
        List all available profiles.

        Returns:
            List of profile metadata
        """
        return self.file_handler.list_profiles()

    def get_profile(self, profile_name: str) -> ProfileData:
        """
        Get a profile by name.

        Args:
            profile_name: Name of the profile

        Returns:
            Profile data

        Raises:
            FileNotFoundError: If the profile does not exist
        """
        return self.file_handler.read_profile(profile_name)

    def save_profile(self, profile_name: str, profile_data: ProfileData) -> None:
        """
        Save a profile to disk.

        Args:
            profile_name: Name of the profile
            profile_data: Profile data to save

        Raises:
            ValueError: If the profile data is invalid
        """
        self.file_handler.write_profile(profile_name, profile_data)

    def create_profile(self, profile_name: str, template_profile: str | None = None) -> ProfileData:
        """
        Create a new profile, optionally using an existing profile as a template.

        Args:
            profile_name: Name of the new profile
            template_profile: Optional name of an existing profile to use as template

        Returns:
            New profile data

        Raises:
            FileExistsError: If the profile already exists
            FileNotFoundError: If the template profile does not exist
        """
        template_data = None

        if template_profile:
            template = self.file_handler.read_profile(template_profile)
            template_data = template.to_yaml()
            # Update Profile field with new name
            template_data["Profile"] = profile_name

        return self.file_handler.create_profile(profile_name, template_data)

    def delete_profile(self, profile_name: str) -> None:
        """
        Delete a profile.

        Args:
            profile_name: Name of the profile to delete

        Raises:
            FileNotFoundError: If the profile does not exist
        """
        self.file_handler.delete_profile(profile_name)

    def get_editable_fields(self, profile_data: ProfileData) -> list[ProfileField]:
        """
        Get all editable fields from a profile, organized by sections.

        Args:
            profile_data: Profile data

        Returns:
            List of profile fields with section headers
        """
        flattened = flatten_dict(profile_data.raw_data)
        fields: list[ProfileField] = []

        # Track sections for organization
        current_section = None

        for key in sorted(flattened.keys()):
            value = flattened[key]

            # Determine if this is a new section
            parts = key.split(".")
            section = parts[0] if len(parts) > 1 else None

            if section and section != current_section:
                # Add section header
                fields.append(
                    ProfileField(
                        key=section,
                        value="",
                        display_key=f"# {section}",
                        is_section_header=True,
                    )
                )
                current_section = section

            # Add the field
            display_key = self._format_display_key(key)
            display_value = format_yaml_value(value)

            fields.append(
                ProfileField(
                    key=key,
                    value=value,
                    display_key=f"{display_key}: {display_value}",
                    is_section_header=False,
                )
            )

        return fields

    def update_field(self, profile_data: ProfileData, field_key: str, new_value: str) -> ProfileData:
        """
        Update a field in the profile data.

        Args:
            profile_data: Profile data to update
            field_key: Flattened key of the field to update
            new_value: New value (as string, will be converted to appropriate type)

        Returns:
            Updated profile data
        """
        # Convert string value to appropriate type
        converted_value = self._convert_value(new_value)

        # Update the field
        profile_data.set_value(field_key, converted_value)

        return profile_data

    def _format_display_key(self, key: str) -> str:
        """
        Format a flattened key for display.

        Args:
            key: Flattened key (e.g., 'IAM.DeploymentRole')

        Returns:
            Formatted display key with indentation
        """
        parts = key.split(".")

        if len(parts) == 1:
            return key

        # Indent nested keys
        indent = "  " * (len(parts) - 1)
        return f"{indent}{parts[-1]}"

    def _convert_value(self, value_str: str) -> Any:
        """
        Convert a string value to the appropriate Python type.

        Args:
            value_str: String representation of the value

        Returns:
            Converted value
        """
        # Handle empty strings
        if not value_str or value_str.strip() == "":
            return ""

        # Handle null
        if value_str.lower() in ["null", "none"]:
            return None

        # Handle booleans
        if value_str.lower() == "true":
            return True
        if value_str.lower() == "false":
            return False

        # Handle numbers
        try:
            if "." in value_str:
                return float(value_str)
            else:
                return int(value_str)
        except ValueError:
            pass

        # Return as string
        return value_str
