# Mon - Monitoring Configuration Profile Manager

A terminal-based application for managing AWS monitoring YAML configuration profiles with an integrated development dashboard.

## Features

- **Dashboard** - Central hub for profiles, development, and deployment tasks
- **Profile Management** - List, view, edit, and create YAML configuration profiles
- **Development Tools** - Quick access to start and test commands
- **Deployment Tools** - Bootstrap, deploy, and destroy with stage selection
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

### Dashboard (Interactive Mode)

Start the interactive dashboard:

```bash
# Using make (recommended)
make mon

# Using the wrapper script directly
./ops/development/mon.sh start

# Using Python module directly
poetry run python -m .main start
```

The dashboard provides quick access to:

```
👤 Profiles
  • 2 profiles

📦 Development
  • start       - Start the local server
  • test        - Run tests with coverage

🚀 Deployment
  • bootstrap   - Prepare S3 and IAM roles
  • deploy      - Deploy to specified stage
  • destroy     - Destroy deployment
```

**Navigation:**
- **↑/↓** - Navigate through menu items
- **Enter** - Select an option
- **Esc** - Exit the application

**Profile Management:**
- Select "Profiles" to view, edit, create, or delete configuration profiles

**Development Commands:**
- Select any dev command to run `make <command>` automatically

**Deployment Commands:**
- Select a deployment action, then enter the stage name (e.g., local, neos)
- Runs `make <action> stage=<stage>` with real-time output

### Direct Commands (Non-Interactive)

For quick, non-interactive operations:

**List All Profiles:**
```bash
./ops/development/mon.sh list
# or
poetry run python -m .main list
```

**View Profile Contents:**
```bash
./ops/development/mon.sh show local
# or
poetry run python -m .main show local
```

### Profile Editor Navigation

When editing a profile in interactive mode:

- **↑/↓** - Navigate through fields
- **Enter** - Edit selected field
- **Esc** - Go back to previous menu
- **Select "💾 Save changes"** - Save and return to profiles list

## Architecture

The application follows hexagonal architecture principles:

```
mon/
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
poetry run python -m .main list

# Test the show command
poetry run python -m .main show local

# Test interactive mode (requires terminal)
poetry run python -m .main start
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
poetry run python -m .main start --config-dir /full/path/to/configs
```

### "Profile not found"

Ensure the profile name is correct (without the `.yml` or `.yaml` extension):

```bash
# Correct
poetry run python -m .main show local

# Incorrect
poetry run python -m .main show local.yml
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
