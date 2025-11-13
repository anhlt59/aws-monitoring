# MonTerm - Monitoring Configuration Profile Manager

A terminal-based application for managing AWS monitoring YAML configuration profiles.

## Features

- **List Profiles** - Display all YAML configuration profiles in a directory
- **View Profiles** - Show the contents of a specific profile
- **Edit Profiles** - Interactive editor for modifying configuration values
- **Create Profiles** - Create new profiles from scratch or from templates
- **Validation** - Automatic YAML structure validation before saving

## Installation

The required dependencies are already defined in `pyproject.toml`. To install them:

```bash
# Install dependencies
poetry install --with local

# Activate the virtual environment
poetry shell
```

## Usage

### Interactive Mode

Start the interactive profile manager:

```bash
# Manage master stack configs (default)
poetry run python -m ops.tools.monterm.main start

# Manage agent stack configs
poetry run python -m ops.tools.monterm.main start --agent

# Custom config directory
poetry run python -m ops.tools.monterm.main start --config-dir /path/to/configs
```

### List All Profiles

List all available profiles in a directory:

```bash
# List master profiles
poetry run python -m ops.tools.monterm.main list

# List agent profiles
poetry run python -m ops.tools.monterm.main list --config-dir infra/agent/configs
```

### View Profile Contents

Display the contents of a specific profile:

```bash
# View a profile
poetry run python -m ops.tools.monterm.main show local

# View from custom directory
poetry run python -m ops.tools.monterm.main show local --config-dir infra/agent/configs
```

## Interactive Mode Navigation

When running in interactive mode, use the following keyboard shortcuts:

- **↑/↓** - Navigate through options
- **Enter** - Select/Edit field
- **Esc** - Go back/Cancel
- **Ctrl+S** - Save changes (in profile editor)

## Architecture

The application follows hexagonal architecture principles:

```
monterm/
├── main.py                 # Entry point with Click CLI
├── adapters/              # External adapters
│   ├── file_handler.py    # YAML file I/O
│   └── terminal_ui.py     # Terminal UI rendering
├── services/              # Business logic
│   └── profile_service.py # Profile management
├── models/                # Data models
│   └── profile.py         # Pydantic models
├── constants.py           # Application constants
└── utils.py               # Utility functions
```

## Configuration Files

The application manages YAML configuration files with the following structure:

```yaml
Region: us-east-1
Profile: local

# AWS Services
IAM:
  DeploymentRole: arn:aws:iam::000000000000:role/monitoring-DeploymentRole

S3:
  DeploymentBucket:
    Name: monitoring-local-deployment

Lambda:
  Environment:
    LOG_LEVEL: DEBUG
  LogRetentionInDays: 7

# ... more configuration
```

## Features in Detail

### Profile Editor

- **Hierarchical Display** - Nested YAML keys are displayed with proper indentation
- **Section Headers** - Automatically groups fields by top-level keys
- **Type Preservation** - Maintains correct data types (strings, numbers, booleans)
- **Validation** - Validates YAML structure before saving

### Supported Field Types

- **Strings** - Text values
- **Numbers** - Integers and floats
- **Booleans** - `true`/`false` values
- **Null** - `null`/`none` values

### Limitations

- Multi-line string editing is limited (will be converted to single line)
- Complex types (lists, dictionaries) cannot be edited directly
- Section headers cannot be modified

## Development

### Adding New Features

1. **Models** - Define data structures in `models/profile.py`
2. **Adapters** - Implement external integrations in `adapters/`
3. **Services** - Add business logic in `services/profile_service.py`
4. **UI** - Update terminal interface in `adapters/terminal_ui.py`
5. **CLI** - Add new commands in `main.py`

### Testing

```bash
# Test the list command
poetry run python -m ops.tools.monterm.main list

# Test the show command
poetry run python -m ops.tools.monterm.main show local

# Test interactive mode (requires terminal)
poetry run python -m ops.tools.monterm.main start
```

## Dependencies

- **click** - Command-line interface framework
- **questionary** - Interactive prompts
- **rich** - Terminal formatting and display
- **pyyaml** - YAML parsing
- **pydantic** - Data validation

## Troubleshooting

### "Configuration directory not found"

Make sure you're running the command from the project root directory, or specify the full path:

```bash
poetry run python -m ops.tools.monterm.main start --config-dir /full/path/to/configs
```

### "Profile not found"

Ensure the profile name is correct (without the `.yml` or `.yaml` extension):

```bash
# Correct
poetry run python -m ops.tools.monterm.main show local

# Incorrect
poetry run python -m ops.tools.monterm.main show local.yml
```

### Import Errors

Make sure you've installed all dependencies:

```bash
poetry install --with local
```

## Contributing

When adding new features or making changes:

1. Follow hexagonal architecture principles
2. Add type hints to all functions
3. Use Pydantic for data validation
4. Update this README with new features
5. Test thoroughly with existing config files

## License

This tool is part of the AWS Monitoring project.
