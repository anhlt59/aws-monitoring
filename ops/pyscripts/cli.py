"""
Entrypoint for the CLI tool.
"""

import sys
from pathlib import Path

from rich import pretty, traceback

BASE_DIR = Path(__file__).parent
sys.path.append(str(BASE_DIR))


def cli():
    traceback.install()
    pretty.install()


def main():
    cli()


if __name__ == "__main__":
    main()
