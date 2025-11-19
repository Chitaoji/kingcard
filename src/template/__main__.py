"""
Contains the cli api of kingcard.

NOTE: this module is private. All functions and objects are available in the main
`kingcard` namespace - use that instead.

"""

import click


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
def run() -> None:
    """Read and display a config file."""
