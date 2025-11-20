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
            init_units = {"k": 1, "n": 2, "i": 5, "s": 2}
        self.init_units = init_units
        self.units = init_units.copy()

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return "".join(f"{k.upper()*v}" for k, v in self.units.items())

    def add(self, tag: str) -> None:
        """Add a unit."""
        self.units[tag] += 1

    def remove(self, tag: str) -> None:
        """Remove a unit."""
        if self.units[tag] > 0:
            self.units[tag] -= 1
        else:
            raise ValueError(f"tag {tag!r} has no units left")
