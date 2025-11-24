"""
Contains the game starter: KingCardGame.

NOTE: this module is private. All functions and objects are available in the main
`kingcard` namespace - use that instead.

"""

from typing import TYPE_CHECKING

from .counter import CardCounter
from .error import CommunicationEnd, CommunicationRestart, GameOver
from .io import IO
from .units import ARMS

if TYPE_CHECKING:
    from .comm import Communicator

__all__ = ["KingCardBattle"]


class KingCardBattle:
    """Start a King-Card battle."""

    def __init__(
        self,
        allies: CardCounter,
        enemies: CardCounter,
        io: IO,
        communicator: "Communicator",
        can_restart: bool = False,
    ) -> None:
        """Initialize."""
        self.round = 0
        self.locked = False

        self.init = allies, enemies
        self.allies = allies
        self.enemies = enemies
        self.io = io
        self.comm = communicator

        self.can_restart = can_restart

    def lock(self) -> None:
        """Lock the status."""
        self.locked = True

    def loop(self) -> None:
        """Loop until the communcation is ended."""
        self.io.double_line()
        self.io.game_start()
        self.io.hint()

        while True:
            try:
                self.next_round()
            except CommunicationEnd:
                break
            except CommunicationRestart:
                self.allies, self.enemies = self.init
                self.round = 0
            except GameOver as e:
                match e.args[0]:
                    case "win":
                        self.io.line()
                        self.io.win_battle()
                    case "lose":
                        self.io.line()
                        self.io.lose_battle()
                    case _:
                        raise e
                self.io.newline()
                self.io.cards_left(self.allies)
                self.round = -1

    def next_round(self) -> None:
        """Communicate with server/client."""
        if self.locked:
            self.locked = False
            msg = self.io.input.action()
        elif self.round == -1:
            self.io.line()
            self.io.game_over()
            self.io.hint_to_restart()
            msg = self.io.input.action()
        else:
            self.round += 1
            if self.round == 1:
                self.io.line()
                self.io.battle_start()
                self.io.show_cards(self.allies)
                self.io.show_cards(self.enemies)
            self.io.line()
            self.io.rount_start(self.round, self.allies, self.enemies)
            msg = self.io.input.action()
        self._check_message(msg)

    def _check_message(self, message: str) -> None:
        if not message.startswith("/"):
            if self.round == -1 or not message:
                self.lock()
                return
            for tag, n in self.allies.units.items():
                if n <= 0:
                    continue
                unit = ARMS[tag]
                if unit.match(message):
                    self.io.play(unit)
                    self.comm.send(unit.tag)
                    enemy = ARMS[self._get_message_from_opponent()]
                    self.io.play(enemy, is_opponent=True)
                    unit.on_round_begin(enemy, self.allies, self.enemies)
                    return
            self.lock()
            return

        match message[1:].lower():
            case "q":
                self.comm.send(message)
                self.io.double_line()
                self.io.wait_exit()
                self.comm.recv()
                self.io.communication_terminated()
                self.comm.close()
                raise CommunicationEnd()
            case "r":
                if self.can_restart:
                    self.comm.send(message)
                    self.io.double_line()
                    self.io.wait_restart()
                    self.comm.recv()
                    raise CommunicationRestart()
                else:
                    self.io.cannot_restart()
                    self.lock()
            case "h":
                self.io.help(0)
                self.lock()

    def _get_message_from_opponent(self) -> str:
        msg = self.comm.recv()
        if not msg.startswith("/"):
            return msg
        match msg[1:].lower():
            case "q":
                self.io.double_line()
                self.io.opponent_exit()
                self.comm.close()
                raise CommunicationEnd()
            case "r":
                self.io.double_line()
                self.io.opponent_restart()
                raise CommunicationRestart()
