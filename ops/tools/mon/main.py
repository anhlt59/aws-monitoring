"""Main CLI application for managing monitoring configuration profiles."""

import sys
from pathlib import Path

import click

from ops.tools.mon.adapters.terminal_ui import TerminalUI
from ops.tools.mon.constants import AGENT_CONFIG_DIR, DEFAULT_CONFIG_DIR
from ops.tools.mon.services.profile import ProfileService


class MonTermApp:
    """Main application class for monterm."""

    def __init__(self, config_dir: Path):
        """
        Initialize the application.

        Args:
            config_dir: Configuration directory path
        """
        self.config_dir = Path(config_dir)
        self.service = ProfileService(self.config_dir)
        self.ui = TerminalUI()

    def run(self) -> None:
        """Run the main application loop."""
        while True:
            try:
                # Get profile count for dashboard
                profiles = self.service.list_profiles()
                profile_count = len(profiles)

                # Show dashboard
                selected_action = self.ui.show_dashboard(profile_count)

                if selected_action is None:
                    # User cancelled
                    break

                # Handle dashboard actions
                if selected_action == "profiles":
                    self._manage_profiles()
                elif selected_action == "dev_start":
                    self.ui.run_command("make start")
                elif selected_action == "dev_test":
                    self.ui.run_command("make test")
                elif selected_action == "deploy_bootstrap":
                    self._run_deploy_command("bootstrap")
                elif selected_action == "deploy_deploy":
                    self._run_deploy_command("deploy")
                elif selected_action == "deploy_destroy":
                    self._run_deploy_command("destroy")

            except KeyboardInterrupt:
                self.ui.show_info("\nExiting...")
                break
            except Exception as e:
                self.ui.show_error(f"An error occurred: {e}")
                self.ui.pause()

    def _manage_profiles(self) -> None:
        """Manage profiles submenu."""
        while True:
            try:
                # List profiles
                profiles = self.service.list_profiles()

                # Select profile
                selected = self.ui.select_profile(profiles, self.config_dir)

                if selected is None:
                    # User cancelled, go back to dashboard
                    break

                if selected == "CREATE_NEW":
                    self._create_new_profile(profiles)
                else:
                    self._edit_profile(selected)

            except Exception as e:
                self.ui.show_error(f"An error occurred: {e}")
                self.ui.pause()

    def _run_deploy_command(self, action: str) -> None:
        """
        Run a deployment command with stage input.

        Args:
            action: Deployment action (bootstrap, deploy, destroy)
        """
        stage = self.ui.prompt_stage_input()

        if not stage:
            return

        # Build the make command with stage parameter
        command = f"{action} stage={stage}"
        self.ui.run_command(command)

    def _create_new_profile(self, existing_profiles: list) -> None:
        """
        Create a new profile.

        Args:
            existing_profiles: List of existing profiles
        """
        # Prompt for profile name
        profile_name = self.ui.prompt_profile_name()

        if not profile_name:
            return

        # Ask if user wants to use a template
        if existing_profiles:
            use_template = self.ui.confirm_action("Would you like to use an existing profile as a template?")

            if use_template:
                template_name = self.ui.select_profile(existing_profiles, include_create=False)

                if template_name:
                    try:
                        self.service.create_profile(profile_name, template_profile=template_name)
                        self.ui.show_success(f"Profile '{profile_name}' created from template '{template_name}'!")
                        self.ui.pause()
                        return
                    except FileExistsError:
                        self.ui.show_error(f"Profile '{profile_name}' already exists.")
                        self.ui.pause()
                        return
                    except Exception as e:
                        self.ui.show_error(f"Failed to create profile: {e}")
                        self.ui.pause()
                        return

        # Create with default template
        try:
            self.service.create_profile(profile_name)
            self.ui.show_success(f"Profile '{profile_name}' created!")
            self.ui.pause()
        except FileExistsError:
            self.ui.show_error(f"Profile '{profile_name}' already exists.")
            self.ui.pause()
        except Exception as e:
            self.ui.show_error(f"Failed to create profile: {e}")
            self.ui.pause()

    def _edit_profile(self, profile_name: str) -> None:
        """
        Edit an existing profile.

        Args:
            profile_name: Name of the profile to edit
        """
        try:
            # Load profile
            profile_data = self.service.get_profile(profile_name)
            profile_path = self.config_dir / f"{profile_name}.yml"
            has_changes = False

            while True:
                # Show editor header
                self.ui.show_profile_editor_header(profile_name, profile_path)

                # Get editable fields
                fields = self.service.get_editable_fields(profile_data)

                # Select field to edit
                selected_field = self.ui.select_field_to_edit(fields)

                if selected_field is None:
                    # User cancelled or went back
                    if has_changes:
                        if self.ui.confirm_action("You have unsaved changes. Save before exiting?"):
                            self._save_profile(profile_name, profile_data)
                    break

                # Check if user wants to save
                if selected_field.key == "__SAVE__":
                    self._save_profile(profile_name, profile_data)
                    has_changes = False
                    continue

                # Edit the field
                new_value = self.ui.edit_field_value(selected_field)

                if new_value is not None:
                    try:
                        # Update the field
                        profile_data = self.service.update_field(profile_data, selected_field.key, new_value)
                        has_changes = True
                        self.ui.show_success(f"Field '{selected_field.key}' updated!")
                    except Exception as e:
                        self.ui.show_error(f"Failed to update field: {e}")

        except FileNotFoundError:
            self.ui.show_error(f"Profile '{profile_name}' not found.")
            self.ui.pause()
        except Exception as e:
            self.ui.show_error(f"Failed to load profile: {e}")
            self.ui.pause()

    def _save_profile(self, profile_name: str, profile_data) -> None:
        """
        Save profile changes.

        Args:
            profile_name: Name of the profile
            profile_data: Profile data to save
        """
        try:
            self.service.save_profile(profile_name, profile_data)
            self.ui.show_success(f"Profile '{profile_name}' saved successfully!")
            self.ui.pause()
        except Exception as e:
            self.ui.show_error(f"Failed to save profile: {e}")
            self.ui.pause()


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Terminal application for managing AWS monitoring YAML configuration profiles."""
    pass


@cli.command()
@click.option(
    "--config-dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default=None,
    help="Configuration directory path (default: infra/master/configs)",
)
@click.option(
    "--agent",
    is_flag=True,
    help="Use agent configuration directory (infra/agent/configs)",
)
def start(config_dir: Path | None, agent: bool) -> None:
    """Start the interactive profile manager."""
    # Determine config directory
    if config_dir is None:
        if agent:
            config_dir = AGENT_CONFIG_DIR
        else:
            config_dir = DEFAULT_CONFIG_DIR

    # Convert to absolute path
    config_dir = config_dir.resolve()

    # Check if directory exists
    if not config_dir.exists():
        click.echo(f"Error: Configuration directory not found: {config_dir}", err=True)
        sys.exit(1)

    # Run the application
    app = MonTermApp(config_dir)
    app.run()


@cli.command()
@click.argument("profile_name")
@click.option(
    "--config-dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default=DEFAULT_CONFIG_DIR,
    help="Configuration directory path",
)
def show(profile_name: str, config_dir: Path) -> None:
    """Show the contents of a profile."""
    try:
        service = ProfileService(config_dir)
        profile_data = service.get_profile(profile_name)

        ui = TerminalUI()
        ui.display_profile_summary(profile_data)

        # Print raw YAML
        import yaml

        click.echo("\n" + "─" * 50)
        click.echo(yaml.dump(profile_data.to_yaml(), default_flow_style=False, sort_keys=False))

    except FileNotFoundError:
        click.echo(f"Error: Profile '{profile_name}' not found.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option(
    "--config-dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default=DEFAULT_CONFIG_DIR,
    help="Configuration directory path",
)
def list(config_dir: Path) -> None:
    """List all available profiles."""
    try:
        service = ProfileService(config_dir)
        profiles = service.list_profiles()

        if not profiles:
            click.echo("No profiles found.")
            return

        click.echo(f"Available profiles ({config_dir}):\n")
        for profile in profiles:
            click.echo(f"  • {profile.name}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


def main():
    """Entry point for the CLI application."""
    cli()


if __name__ == "__main__":
    main()
