"""
Contains error instances.

NOTE: this module is private. All functions and objects are available in the main
`kingcard` namespace - use that instead.

"""

__all__ = []


class CommunicationError(Exception):
    """Communication Error."""


class GameQuit(Exception):
    """Quit the game."""


class BattleRestart(Exception):
    """Battle restart."""


class BattleOver(Exception):
    """Battle over."""
