"""
Contains the definition of arms.

NOTE: this module is private. All functions and objects are available in the main
`kingcard` namespace - use that instead.

"""

__all__ = ["ARMS"]

ARMS = {
    "k": {"name": "king", "level": 4},
    "c": {"name": "cavalier", "level": 3},
    "i": {"name": "infantry", "level": 2},
    "s": {"name": "slave", "level": 1},
}
