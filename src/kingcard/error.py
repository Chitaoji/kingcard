"""
Contains error instances.

NOTE: this module is private. All functions and objects are available in the main
`kingcard` namespace - use that instead.

"""

__all__ = []


class CommunicationError(Exception):
    """Communication Error."""


class CommunicationEnd(Exception):
    """Communication End."""


class CommunicationRestart(Exception):
    """Communication Restart."""


class GameOver(Exception):
    """Game over."""
