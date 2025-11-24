"""
Contains the definition of arms.

NOTE: this module is private. All functions and objects are available in the main
`kingcard` namespace - use that instead.

"""

from typing import TYPE_CHECKING, Self

from .error import GameOver

if TYPE_CHECKING:
    from .counter import CardCounter
    from .io import IO

__all__ = []


class Unit:
    """Defines units."""

    tag: str
    rank: int
    io: "IO"

    @property
    def fullname(self):
        """Fullname"""
        return self.__class__.__name__

    def match(self, name: str) -> bool:
        """Match the card-name."""
        upper_name = name.upper()
        return upper_name == self.tag or upper_name == self.fullname.upper()

    def is_a(self, unit_type: type) -> bool:
        """Returns whether this unit is of `unit_type`."""
        return isinstance(self, unit_type)

    def on_round_begin(
        self, enemy: Self, allies: "CardCounter", enemies: "CardCounter"
    ) -> None:
        """Actions on the begining of round."""
        self.io.newline()
        self.on_fight(enemy, allies, enemies)
        enemy.on_fight(self, enemies, allies)

    def on_fight(
        self, enemy: Self, allies: "CardCounter", enemies: "CardCounter"
    ) -> None:
        """Actions on the battle."""
        if enemy.rank < self.rank:
            enemy.on_destroyed(self, enemies, allies)
        elif enemy.rank == self.rank:
            enemy.on_draw(self, enemies, allies)

    def on_draw(
        self, enemy: Self, allies: "CardCounter", enemies: "CardCounter"
    ) -> None:
        """Actions on draw."""
        _ = enemy, enemies
        if allies.is_opponent:
            self.io.both_destroyed()
        allies.remove(self.tag)

    def on_destroyed(
        self, enemy: Self, allies: "CardCounter", enemies: "CardCounter"
    ) -> None:
        """Actions on being destroyed."""
        _ = enemy, enemies
        self.io.defeat(self, allies.is_opponent)
        allies.remove(self.tag)

    def on_captured(
        self, enemy: Self, allies: "CardCounter", enemies: "CardCounter"
    ) -> None:
        """Actions on being captured."""
        _ = enemy
        self.io.capture(self, allies.is_opponent)
        allies.remove(self.tag)
        enemies.add(self.tag)


class King(Unit):
    """King."""

    tag = "K"
    rank = 5

    def on_draw(self, enemy: Self, allies, enemies) -> None:
        """Actions on draw."""
        if allies.is_opponent:
            if enemy.is_a(King):
                self.io.both_return()
            else:
                enemy.on_destroyed(self, enemies, allies)

    def on_destroyed(self, enemy, allies, enemies) -> None:
        super().on_destroyed(enemy, allies, enemies)
        if allies.is_opponent:
            raise GameOver("win")
        raise GameOver("lose")


class Knight(Unit):
    """Knight."""

    tag = "N"
    rank = 4

    def on_fight(self, enemy: Self, allies, enemies) -> None:
        """Actions on meeting the enemy."""
        if enemy.is_a(Slave):
            self.io.both_return()
        else:
            super().on_fight(enemy, allies, enemies)


class Infantry(Unit):
    """Infantry."""

    tag = "I"
    rank = 3


class Militia(Unit):
    """Militia."""

    tag = "M"
    rank = 2

    def on_fight(self, enemy: Self, allies, enemies) -> None:
        if enemy.rank == 1:
            enemy.on_captured(self, enemies, allies)
        else:
            super().on_fight(enemy, allies, enemies)


class Slave(Unit):
    """Slave."""

    tag = "S"
    rank = 1

    def on_fight(self, enemy: Self, allies, enemies) -> None:
        if enemy.rank == 5:
            enemy.on_destroyed(self, enemies, allies)
        else:
            super().on_fight(enemy, allies, enemies)

    def on_destroyed(self, enemy: Self, allies, enemies) -> None:
        if enemy.rank == 5:
            return
        super().on_destroyed(enemy, allies, enemies)


ARMS: dict[str, Unit] = {
    King.tag: King(),
    Knight.tag: Knight(),
    Infantry.tag: Infantry(),
    Militia.tag: Militia(),
    Slave.tag: Slave(),
}


def set_unit_io(io: "IO") -> None:
    """Set io for the units."""
    for unit in ARMS.values():
        unit.io = io
