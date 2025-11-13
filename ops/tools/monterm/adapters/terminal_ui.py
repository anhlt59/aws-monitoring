"""Terminal UI adapter for interactive user interface."""

from pathlib import Path

import questionary
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ops.tools.monterm.models.profile import ProfileData, ProfileField, ProfileMetadata


class TerminalUI:
    """Terminal user interface adapter."""

    def __init__(self):
        """Initialize the terminal UI."""
        self.console = Console()

    def show_profiles_list(self, profiles: list[ProfileMetadata], config_dir: Path) -> None:
        """
        Display a list of profiles.

        Args:
            profiles: List of profile metadata
            config_dir: Configuration directory path
        """
        self.console.clear()
        self.console.print("🖥️  Profiles\n", style="bold cyan")
        self.console.print(f"{len(profiles)} profiles ({config_dir})\n")

    def select_profile(self, profiles: list[ProfileMetadata], include_create: bool = True) -> str | None:
        """
        Show an interactive profile selector.

        Args:
            profiles: List of available profiles
            include_create: Whether to include "Create new profile" option

        Returns:
            Selected profile name, "CREATE_NEW", or None if cancelled
        """
        choices = [profile.name for profile in profiles]

        if include_create:
            choices.append("Create new profile")

        selected = questionary.select(
            "",
            choices=choices,
            instruction="Press ↑↓ to navigate · Enter to select · Esc to go back",
        ).ask()

        if selected is None:
            return None

        if selected == "Create new profile":
            return "CREATE_NEW"

        return selected

    def show_profile_editor_header(self, profile_name: str, profile_path: Path) -> None:
        """
        Display the profile editor header.

        Args:
            profile_name: Name of the profile being edited
            profile_path: Path to the profile file
        """
        self.console.clear()
        self.console.print("⚙️  Profile Editor\n", style="bold cyan")
        self.console.print(f"{profile_name} ({profile_path})\n")

    def select_field_to_edit(self, fields: list[ProfileField]) -> ProfileField | None:
        """
        Show an interactive field selector for editing.

        Args:
            fields: List of profile fields

        Returns:
            Selected field, or None if cancelled
        """
        # Filter out section headers for selection
        editable_fields = [f for f in fields if not f.is_section_header]

        if not editable_fields:
            self.show_error("No editable fields found in this profile.")
            return None

        # Create choices with display keys
        choices = []
        for field in fields:
            if field.is_section_header:
                choices.append(questionary.Separator(field.display_key))
            else:
                choices.append(
                    questionary.Choice(
                        title=field.display_key,
                        value=field.key,
                    )
                )

        choices.append(questionary.Separator())
        choices.append(questionary.Choice(title="← Back to profiles", value="BACK"))
        choices.append(questionary.Choice(title="💾 Save changes", value="SAVE"))

        selected_key = questionary.select(
            "",
            choices=choices,
            instruction="Press ↑↓ to navigate · Enter to edit · Esc to go back",
        ).ask()

        if selected_key is None or selected_key == "BACK":
            return None

        if selected_key == "SAVE":
            # Return a special marker
            return ProfileField(
                key="__SAVE__",
                value="",
                display_key="Save",
                is_section_header=False,
            )

        # Find the selected field
        for field in editable_fields:
            if field.key == selected_key:
                return field

        return None

    def edit_field_value(self, field: ProfileField) -> str | None:
        """
        Show an input prompt to edit a field value.

        Args:
            field: Field to edit

        Returns:
            New value, or None if cancelled
        """
        # Format the current value for display
        from ops.tools.monterm.utils import format_yaml_value

        current_value = format_yaml_value(field.value)

        # Handle multi-line values
        if isinstance(field.value, str) and "\n" in field.value:
            self.show_info("Multi-line editing is not supported yet. Value will be converted to single line.")
            current_value = field.value.replace("\n", " ")

        # Handle complex types (lists, dicts)
        if isinstance(field.value, (list, dict)):
            self.show_error("Complex types (lists, dictionaries) cannot be edited directly.")
            return None

        # Show input prompt
        new_value = questionary.text(
            f"Edit {field.key}:",
            default=str(current_value) if current_value else "",
            instruction="Enter new value · Esc to cancel",
        ).ask()

        return new_value

    def prompt_profile_name(self, default: str = "") -> str | None:
        """
        Prompt for a new profile name.

        Args:
            default: Default value

        Returns:
            Profile name, or None if cancelled
        """
        name = questionary.text(
            "Enter profile name:",
            default=default,
            instruction="Enter name · Esc to cancel",
            validate=lambda text: len(text) > 0 or "Profile name cannot be empty",
        ).ask()

        return name

    def confirm_action(self, message: str) -> bool:
        """
        Show a confirmation prompt.

        Args:
            message: Confirmation message

        Returns:
            True if confirmed, False otherwise
        """
        result = questionary.confirm(message, default=False).ask()
        return result if result is not None else False

    def show_success(self, message: str) -> None:
        """
        Display a success message.

        Args:
            message: Success message
        """
        self.console.print(f"✅ {message}", style="bold green")

    def show_error(self, message: str) -> None:
        """
        Display an error message.

        Args:
            message: Error message
        """
        self.console.print(f"❌ {message}", style="bold red")

    def show_info(self, message: str) -> None:
        """
        Display an info message.

        Args:
            message: Info message
        """
        self.console.print(f"ℹ️  {message}", style="bold blue")

    def show_warning(self, message: str) -> None:
        """
        Display a warning message.

        Args:
            message: Warning message
        """
        self.console.print(f"⚠️  {message}", style="bold yellow")

    def display_profile_summary(self, profile_data: ProfileData) -> None:
        """
        Display a summary of the profile data.

        Args:
            profile_data: Profile data to display
        """
        table = Table(title="Profile Summary", show_header=True, header_style="bold magenta")
        table.add_column("Field", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")

        table.add_row("Region", profile_data.region or "N/A")
        table.add_row("Profile", profile_data.profile or "N/A")

        self.console.print(table)

    def pause(self) -> None:
        """Pause and wait for user input."""
        questionary.press_any_key_to_continue().ask()
