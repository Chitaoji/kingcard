"""
Contains the core of kingcard: KingCardSimulator, etc.

NOTE: this module is private. All functions and objects are available in the main
`kingcard` namespace - use that instead.

"""

from .battle import KingCardBattle
from .cards import set_cards_io
from .comm import TcpCommunicator
from .counter import CardCounter
from .error import BattleRestart, GameQuit
from .io import IO

__all__ = ["KingCardSimulator"]


class KingCardSimulator:
    """Simulator of the King-Card game."""

    def __init__(self) -> None:
        """Initialize."""
        self.io = IO()
        self.io.input.command = self.command
        set_cards_io(self.io)

        self.io.game_start()
        self.io.hint()
        self.io.line()
        self.is_quick_game = False

        self.comm = TcpCommunicator(self.io)

    def start_a_game(self) -> None:
        """Start a game."""
        self.is_quick_game = True
        KingCardBattle(
            CardCounter(), CardCounter(None, True), self.io, self.comm
        ).loop()
        self.is_quick_game = False

    def command(self, message: str) -> None:
        """System io."""
        match message[1:]:
            case "q":
                self.comm.send(message)
                self.io.double_line()
                self.io.wait_exit()
                self.comm.recv()
                self.io.communication_terminated()
                self.comm.close()
                raise GameQuit()
            case "r":
                if self.is_quick_game:
                    self.comm.send(message)
                    self.io.double_line()
                    self.io.wait_restart()
                    self.comm.recv()
                    raise BattleRestart()
                self.io.cannot_restart()
            case "h":
                self.io.help(0)
