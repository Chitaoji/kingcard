"""
Contains a counter.

NOTE: this module is private. All functions and objects are available in the main
`kingcard` namespace - use that instead.

"""

__all__ = ["CardCounter"]


class CardCounter:
    """Count the cards."""

    def __init__(
        self, initial: dict[str, int] | None = None, is_opponent: bool = False
    ) -> None:
        if initial is None:
            initial = {"K": 1, "N": 1, "I": 2, "M": 4, "S": 2}
        self.init = initial
        self.cards = initial.copy()
        self.is_opponent = is_opponent

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return "".join(
            k.upper() * v if v <= 3 else f"({k.upper()}x{v})"
            for k, v in self.cards.items()
        )

    def add(self, tag: str) -> None:
        """Add a card."""
        self.cards[tag] += 1

    def remove(self, tag: str) -> None:
        """Remove a card."""
        if self.cards[tag] > 0:
            self.cards[tag] -= 1
        else:
            raise ValueError(f"tag {tag!r} has no cards left")
