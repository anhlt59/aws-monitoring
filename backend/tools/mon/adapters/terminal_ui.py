"""Terminal UI adapter for interactive user interface."""

from pathlib import Path
from typing import Any, Sequence, Union

import questionary
from questionary import Choice, Question, Separator, Style
from rich.console import Console
from rich.table import Table

from ..models.profile import ProfileData, ProfileField, ProfileMetadata
from ..utils import execute_command


class TerminalUI:
    """Terminal user interface adapter."""

    def __init__(self):
        """Initialize the terminal UI."""
        self.console = Console()
        self.default_style = Style(
            [
                ("qmark", "fg:#673ab7 bold"),  # token in front of the question
                ("question", "bold"),  # question text
                ("answer", "fg:#f44336 bold"),  # submitted answer text behind the question
                ("pointer", "fg:#673ab7 bold"),  # pointer used in select and checkbox prompts
                ("highlighted", "fg:#673ab7 bold"),  # pointed-at choice in select and checkbox prompts
                ("selected", "fg:#cc5454"),  # style for a selected item of a checkbox
                ("separator", "fg:#00FFFF"),  # separator in lists
                ("instruction", "fg:#858585 italic"),  # user instructions for select, rawselect, checkbox
                ("text", ""),  # plain text
                ("disabled", "fg:#858585 italic"),  # disabled choices for select and checkbox prompts
            ]
        )

    def _make_select_question(
        self,
        choices: Sequence[Union[str, Choice, dict[str, Any]]],
        header: str = "📊 AWS monitoring",
        footer: str = "Press ↑↓ to navigate · Enter to select · Ctrl+C to exit",
    ) -> Question:
        choices = [*choices, Choice(title="\n", value="exit", disabled=footer)]
        return questionary.select(
            header, choices=choices, style=self.default_style, qmark="", instruction=" ", pointer="▶"
        )

    def show_dashboard(self, profile_count: int) -> str | None:
        """
        Display the main dashboard menu.
        Args:
            profile_count: Number of available profiles
        Returns:
            Selected menu option or None if cancelled
        """
        self.console.clear()
        return self._make_select_question(
            choices=[
                Separator("👤  Profiles"),
                Choice(title=f" • {profile_count} profiles", value="profiles"),
                Separator("📦  Development"),
                Choice(title=" • start", value="dev_start"),
                Choice(title=" • test", value="dev_test"),
                Separator("🚀  Deployment"),
                Choice(title=" • bootstrap", value="deploy_bootstrap"),
                Choice(title=" • deploy", value="deploy_deploy"),
                Choice(title=" • destroy", value="deploy_destroy"),
            ]
        ).ask()

    def select_profile(self, profiles: list[ProfileMetadata], config_dir: Path) -> str | None:
        """
        Show an interactive profile selector.
        Args:
            profiles: List of available profiles
            config_dir: Configuration directory path
        Returns:
            Selected profile name, "CREATE_NEW", or None if cancelled
        """
        self.console.clear()
        return self._make_select_question(
            choices=[
                Separator(f"👤  {len(profiles)} Profiles"),
                *[Choice(title=f" • {profile.name}", value=profile.name) for profile in profiles],
                Choice(" ✚ Create new profile", value="CREATE_NEW"),
            ],
        ).ask()

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
                choices.append(Separator(field.display_key))
            else:
                choices.append(
                    Choice(
                        title=field.display_key,
                        value=field.key,
                    )
                )

        choices.append(Separator())
        choices.append(Choice(title="← Back to profiles", value="BACK"))
        choices.append(Choice(title="💾 Save changes", value="SAVE"))

        selected_key = questionary.select(
            "",
            choices=choices,
            style=self.default_style,
            instruction="Press ↑↓ to navigate · Enter to select · Ctrl+C to go back",
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
        from .utils import format_yaml_value

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
            style=self.default_style,
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
            validate=lambda text: len(text) > 0 or "Profile name cannot be empty",
            style=self.default_style,
            instruction="Enter name · Ctrl+C to cancel",
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
        result = questionary.confirm(message, default=False, qmark="").ask()
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

    def run_command(self, command: str) -> None:
        """
        Run a make command and display the output.

        Args:
            command: Make command to run (e.g., 'start', 'test')
        """
        self.console.clear()
        self.console.print(f"🚀 Running: {command}", style="bold cyan")
        self.console.print("─" * 50)

        try:
            return_code = execute_command(command)

            self.console.print("\n" + "─" * 50)
            if return_code == 0:
                self.show_success(f"Command '{command}' completed successfully!")
            else:
                self.show_error(f"Command '{command}' failed with exit code {return_code}")

        except Exception as e:
            self.show_error(f"Failed to run command: {e}")

        self.pause()

    def prompt_stage_input(self) -> str | None:
        """
        Prompt for stage name (e.g., local, dev, prod).

        Returns:
            Stage name or None if cancelled
        """

        stage = questionary.text(
            "Stage:",
            default="local",
            validate=lambda text: len(text) > 0 or "Stage name cannot be empty",
            style=self.default_style,
            instruction="Enter stage name (e.g., local, neos) · Ctrl+C to cancel",
        ).ask()

        return stage
