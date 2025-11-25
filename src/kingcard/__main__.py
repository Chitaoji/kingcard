"""
Contains the cli api of kingcard.

NOTE: this module is private. All functions and objects are available in the main
`kingcard` namespace - use that instead.

"""

import click

from .core import KingCardSimulator
from .error import CommunicationError, GameQuit


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
def run() -> None:
    """Start a king-card game."""
    try:
        simulator = KingCardSimulator()
        simulator.start_a_game()
    except (CommunicationError, GameQuit):
        pass
