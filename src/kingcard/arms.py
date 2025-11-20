"""
Contains the definition of arms.

NOTE: this module is private. All functions and objects are available in the main
`kingcard` namespace - use that instead.

"""

from typing import Self

from .counter import UnitsCounter
from .error import GameOver

__all__ = ["ARMS"]


class Unit:
    """Defines units."""

    tag: str
    level: int

    @property
    def fullname(self):
        """Fullname"""
        return self.__class__.__name__

    def match(self, name: str) -> bool:
        """Match the card-name."""
        lower_name = name.lower()
        return lower_name == self.tag or lower_name == self.fullname.lower()

    def on_round_begin(
        self, enemy: Self, units: UnitsCounter, enemies: UnitsCounter
    ) -> None:
        """Actions on the begining of round."""
        self.on_battle(enemy, units, enemies)
        enemy.on_battle(self, enemies, units, True)

    def on_battle(
        self,
        enemy: Self,
        units: UnitsCounter,
        enemies: UnitsCounter,
        is_enemy: bool = False,
    ) -> None:
        """Actions on the battle."""
        if enemy.level < self.level:
            enemy.on_destroyed(enemies, units, not is_enemy)
        elif enemy.level == self.level:
            enemy.on_draw(enemies, units, not is_enemy)

    def on_draw(
        self, units: UnitsCounter, enemies: UnitsCounter, is_enemy: bool = False
    ) -> None:
        """Actions on draw."""
        _ = enemies
        if is_enemy:
            print("\n    Both were destroyed.")
        units.remove(self.tag)

    def on_destroyed(
        self, units: UnitsCounter, enemies: UnitsCounter, is_enemy: bool = False
    ) -> None:
        """Actions on being destroyed."""
        _ = enemies
        if is_enemy:
            print(f"\n    Enemy's {self.fullname} was defeated.")
        else:
            print(f"\n    Your {self.fullname} was defeated.")
        units.remove(self.tag)


class King(Unit):
    """King."""

    tag = "k"
    level = 4

    def on_battle(
        self,
        enemy: Self,
        units: UnitsCounter,
        enemies: UnitsCounter,
        is_enemy: bool = False,
    ) -> None:
        """Actions on meeting the enemy."""
        if enemy.level == 1:
            pass
        else:
            super().on_battle(enemy, units, enemies, is_enemy)

    def on_draw(
        self, units: UnitsCounter, enemies: UnitsCounter, is_enemy: bool = False
    ) -> None:
        """Actions on draw."""
        if is_enemy:
            print("\n    Both returned back.")

    def on_destroyed(self, units, enemies, is_enemy=False) -> None:
        super().on_destroyed(units, enemies, is_enemy)
        if is_enemy:
            raise GameOver("win")
        raise GameOver("lose")


class Knight(Unit):
    """Cavalier."""

    tag = "n"
    level = 3

    def on_battle(
        self,
        enemy: Self,
        units: UnitsCounter,
        enemies: UnitsCounter,
        is_enemy: bool = False,
    ) -> None:
        """Actions on meeting the enemy."""
        if enemy.level == 1:
            print("\n    Nothing happens.")
        else:
            super().on_battle(enemy, units, enemies, is_enemy)


class Infantry(Unit):
    """Cavalier."""

    tag = "i"
    level = 2


class Slave(Unit):
    """Cavalier."""

    tag = "s"
    level = 1

    def on_battle(self, enemy: Self, units, enemies, is_enemy=False) -> None:
        if enemy.level == 4:
            enemy.on_destroyed(enemies, units, not is_enemy)
        else:
            super().on_battle(enemy, units, enemies, is_enemy)

    def on_draw(
        self, units: UnitsCounter, enemies: UnitsCounter, is_enemy: bool = False
    ) -> None:
        """Actions on draw."""
        if is_enemy:
            print("    Both returned back.")

    def on_destroyed(self, units, enemies, is_enemy=False) -> None:
        if is_enemy:
            print(f"\n    You captured Enemy's {self.fullname}.")
        else:
            print(f"\n    Enemy captured your {self.fullname}.")
        units.remove(self.tag)
        enemies.add(self.tag)


ARMS: dict[str, Unit] = {"k": King(), "n": Knight(), "i": Infantry(), "s": Slave()}
