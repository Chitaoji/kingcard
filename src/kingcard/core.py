"""
Contains the core of kingcard: KingCardSimulator, etc.

NOTE: this module is private. All functions and objects are available in the main
`kingcard` namespace - use that instead.

"""

from .battle import KingCardBattle
from .comm import TcpCommunicator
from .counter import CardCounter
from .io import IO
from .units import set_unit_io

__all__ = ["KingCardSimulator"]


class KingCardSimulator:
    """Simulator of the King-Card game."""

    def __init__(self) -> None:
        """Initialize."""
        self.io = IO()
        self.comm = TcpCommunicator(self.io)

        set_unit_io(self.io)

    def start_a_game(self) -> None:
        """Start a game."""
        KingCardBattle(
            CardCounter(), CardCounter(None, True), self.io, self.comm, can_restart=True
        ).loop()
