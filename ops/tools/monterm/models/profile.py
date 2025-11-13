"""Data models for configuration profiles."""

from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator


class ProfileMetadata(BaseModel):
    """Metadata for a configuration profile."""

    name: str = Field(..., description="Profile name (without extension)")
    path: Path = Field(..., description="Full path to the profile file")
    exists: bool = Field(default=True, description="Whether the file exists")

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        """Validate profile name."""
        if not value or not value.strip():
            raise ValueError("Profile name cannot be empty")
        return value.strip()

    @field_validator("path")
    @classmethod
    def validate_path(cls, value: Path) -> Path:
        """Validate path is a Path object."""
        if not isinstance(value, Path):
            return Path(value)
        return value


class ProfileData(BaseModel):
    """Data model for a configuration profile."""

    region: str | None = Field(default=None, alias="Region", description="AWS Region")
    profile: str | None = Field(default=None, alias="Profile", description="Profile name")
    raw_data: dict[str, Any] = Field(default_factory=dict, description="Raw YAML data")

    class Config:
        """Pydantic configuration."""

        populate_by_name = True
        arbitrary_types_allowed = True

    @classmethod
    def from_yaml(cls, data: dict[str, Any]) -> "ProfileData":
        """
        Create a ProfileData instance from YAML data.

        Args:
            data: Raw YAML data as dictionary

        Returns:
            ProfileData instance
        """
        return cls(
            region=data.get("Region"),
            profile=data.get("Profile"),
            raw_data=data,
        )

    def to_yaml(self) -> dict[str, Any]:
        """
        Convert ProfileData to YAML-compatible dictionary.

        Returns:
            Dictionary ready for YAML serialization
        """
        return self.raw_data

    def get_flattened_keys(self) -> list[str]:
        """
        Get all flattened keys from the profile data.

        Returns:
            List of flattened keys (e.g., ['Region', 'Profile', 'IAM.DeploymentRole'])
        """
        from ops.tools.monterm.utils import flatten_dict

        flattened = flatten_dict(self.raw_data)
        return sorted(flattened.keys())

    def get_value(self, key: str) -> Any:
        """
        Get a value from the profile data using a flattened key.

        Args:
            key: Flattened key (e.g., 'IAM.DeploymentRole')

        Returns:
            Value at the specified key path
        """
        from ops.tools.monterm.utils import flatten_dict

        flattened = flatten_dict(self.raw_data)
        return flattened.get(key)

    def set_value(self, key: str, value: Any) -> None:
        """
        Set a value in the profile data using a flattened key.

        Args:
            key: Flattened key (e.g., 'IAM.DeploymentRole')
            value: New value to set
        """
        from ops.tools.monterm.utils import flatten_dict, unflatten_dict

        flattened = flatten_dict(self.raw_data)
        flattened[key] = value
        self.raw_data = unflatten_dict(flattened)


class ProfileField(BaseModel):
    """Represents an editable field in a profile."""

    key: str = Field(..., description="Flattened key path")
    value: Any = Field(..., description="Current value")
    display_key: str = Field(..., description="Display name for the key")
    is_section_header: bool = Field(default=False, description="Whether this is a section header")

    @field_validator("key")
    @classmethod
    def validate_key(cls, value: str) -> str:
        """Validate key is not empty."""
        if not value:
            raise ValueError("Key cannot be empty")
        return value
