"""
Contains a counter of arms: UnitCounter.

NOTE: this module is private. All functions and objects are available in the main
`kingcard` namespace - use that instead.

"""

__all__ = ["UnitsCounter"]


class UnitsCounter:
    """Count the units."""

    def __init__(self, init_units: dict[str, int] | None = None) -> None:
        if init_units is None:
            init_units = {"k": 1, "c": 2, "i": 5, "s": 2}
        self.init_nums = init_units
        self.units = init_units.copy()

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return " ".join(f"{v}{k.upper()}" for k, v in self.init_nums.items())

    def add(self, mark: str) -> None:
        """Add a unit."""
        self.units[mark] += 1

    def destroy(self, mark: str) -> None:
        """Destroy a unit."""
        if self.units[mark] > 0:
            self.units[mark] -= 1
