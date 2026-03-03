"""
Contains the core of kingcard: KingCardSimulator, etc.

NOTE: this module is private. All functions and objects are available in the main
`kingcard` namespace - use that instead.

"""

from .battle import KingCardBattle
from .cards import set_cards_io
from .comm import AiCommunicator, Communicator, TcpCommunicator
from .counter import CardCounter
from .error import BattleRestart, GameQuit
from .io import IO

__all__ = ["KingCardSimulator"]


class KingCardSimulator:
    """Simulator of the King-Card game."""

    def __init__(self) -> None:
        """Initialize."""
        self.io = IO()
        self.io.input.command_behaviour = self.command_behaviour
        set_cards_io(self.io)

        self.io.game_start()
        self.io.hint()
        self.io.line()
        self.is_quick_game = False

        self.comm = Communicator(self.io)
        self.io.start_single_mode()
        self.is_single_mode = self.io.input.yes_or_no()
        if not self.is_single_mode:
            self.comm = TcpCommunicator(self.io)

    def start_a_quick_game(self) -> None:
        """Start a quick game."""
        self.is_quick_game = True
        allies = CardCounter()
        enemies = CardCounter(None, True)
        if self.is_single_mode:
            self.comm = AiCommunicator(self.io, enemies)
        KingCardBattle(allies, enemies, self.io, self.comm).loop()
        self.is_quick_game = False

    def command_behaviour(self, message: str) -> None:
        """Behaviour when receiving commands."""
        match message[1:]:
            case "q":
                self.comm.send(message)
                self.io.double_line()
                self.io.wait_for_exit()
                self.comm.recv_only()
                self.io.communication_terminated()
                self.comm.close()
                raise GameQuit()
            case "r":
                if self.is_quick_game:
                    self.comm.send(message)
                    self.io.double_line()
                    self.io.wait_for_restart()
                    self.comm.recv()
                    raise BattleRestart()
                self.io.cannot_restart()
            case "h":
                self.io.help(0)
