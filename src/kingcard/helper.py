"""
Contains help infomation.

NOTE: this module is private. All functions and objects are available in the main
`kingcard` namespace - use that instead.

"""

__all__ = []

MAINPAGE = """
～～～～～～～～～～～～～～～～～～～～～～～～～～～～～～～～～～
Commands:
/h : help
/q : quit the game
/r : restart the game (only in quick-game mode)

Units:
   Name      Rank                Ability    
K  King      V     Survives in battles with other Rank-V units.
N  Knight    IV    Never battles with a slave.
I  Infantry  III   Just an infantry.
M  Militia   II    Captures Rank-I units.
S  Slave     I     Defeats Rank-V units.
～～～～～～～～～～～～～～～～～～～～～～～～～～～～～～～～～～
""".strip()
