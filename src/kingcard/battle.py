"""
Contains the game starter: KingCardGame.

NOTE: this module is private. All functions and objects are available in the main
`kingcard` namespace - use that instead.

"""

from typing import TYPE_CHECKING

from .cards import ARMS, Card
from .counter import CardCounter
from .error import BattleOver, BattleRestart
from .io import IO

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
    ) -> None:
        """Initialize."""
        self.round = 0

        self.init = allies, enemies
        self.allies = allies
        self.enemies = enemies
        self.io = io
        self.comm = communicator

    def loop(self) -> CardCounter:
        """Loop until the communcation is ended."""
        while True:
            try:
                self.next_round()
            except BattleRestart:
                self.allies, self.enemies = self.init
                self.round = 0
            except BattleOver as e:
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
        if self.round == -1:
            self.io.line()
            self.io.battle_over()
            self.io.hint_to_restart()
            card = self.io.input.command(
                {tag: ARMS[tag] for tag, n in self.allies.cards.items() if n > 0}
            )
        else:
            self.round += 1
            if self.round == 1:
                self.io.double_line()
                self.io.battle_start()
                self.io.show_cards(self.allies)
                self.io.show_cards(self.enemies)
            self.io.line()
            self.io.round_start(self.round, self.allies, self.enemies)
            card: Card = self.io.input.card(
                {tag: ARMS[tag] for tag, n in self.allies.cards.items() if n > 0}
            )

        self.io.play(card)
        self.comm.send(card.tag)
        enemy = ARMS[self.comm.recv()]
        self.io.play(enemy, is_opponent=True)
        card.on_round_begin(enemy, self.allies, self.enemies)
