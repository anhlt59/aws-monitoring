"""
Entrypoint for the CLI tool.
"""

import sys
from pathlib import Path

import click
from rich import pretty, traceback

BASE_DIR = Path(__file__).parent
sys.path.append(str(BASE_DIR))


def install_context(ctx: click.Context):
    ctx.ensure_object(dict)
    ctx.obj["session"] = "session"
    return ctx


@click.group()
@click.option("--debug/--no-debug", default=False, required=False, help="Enable debug mode.")
@click.pass_context
def cli(ctx, debug):
    if debug:
        traceback.install()
    pretty.install()
    install_context(ctx)

    @ctx.call_on_close
    def close():
        print("Exiting CLI tool.")


def main():
    # cli.add_command(command)
    cli()


if __name__ == "__main__":
    main()
