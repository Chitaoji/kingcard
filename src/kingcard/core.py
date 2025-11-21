"""
Contains the core of kingcard: KingCardSimulator, etc.

NOTE: this module is private. All functions and objects are available in the main
`kingcard` namespace - use that instead.

"""

from .arms import set_unit_io
from .counter import CardCounter
from .game import KingCardGame, TcpCommunicator
from .io import IO

__all__ = ["KingCardSimulator"]


class KingCardSimulator:
    """Simulator of the King-Card game."""

    def __init__(self) -> None:
        """Initialize."""
        self.io = IO()
        set_unit_io(self.io)

    def start_a_game(self) -> None:
        """Start a game."""
        KingCardGame(
            CardCounter(), CardCounter(None, True), self.io, TcpCommunicator(self.io)
        ).loop()
