"""
Contains display utils.

NOTE: this module is private. All functions and objects are available in the main
`kingcard` namespace - use that instead.

"""

from pathlib import Path
from time import sleep
from typing import TYPE_CHECKING, Callable, TypeVar

from . import helper

if TYPE_CHECKING:
    from .counter import CardCounter
    from .units import Unit


__all__ = []


T = TypeVar("T")


def title(method: T) -> T:
    """Print titles."""

    def wrapper(*args, **kwargs):
        if len(args) == 1 and not kwargs:
            print(method.__doc__)
        else:
            method(*args, **kwargs)
        IO.sleep()

    return wrapper


def info(method: T) -> T:
    """Print info."""

    def wrapper(*args, **kwargs):
        if len(args) == 1 and not kwargs:
            print("    " + method.__doc__)
        else:
            method(*args, **kwargs)
        IO.sleep()

    return wrapper


def error(method: T) -> T:
    """Print errors."""

    def wrapper(*args, **kwargs):
        if len(args) == 1 and not kwargs:
            print("[Error] " + method.__doc__)
        else:
            method(*args, **kwargs)

    return wrapper


def title_input(method: Callable[[T], None]) -> Callable[[T], str]:
    """Print the title and receive input."""

    def wrapper(*_):
        return input(method.__doc__ + " ").lower()

    return wrapper


def info_input(method: Callable[[T], None]) -> Callable[[T], str]:
    """Print some info and receive input."""

    def wrapper(*_):
        return input("    " + method.__doc__ + " ").lower()

    return wrapper


class IO:
    """Print things (by default in English)."""

    LINE = "-" * 50
    DOUBLE_LINE = "=" * 50
    SLEEP_TIME = 0.6
    SNAP_TIME = 0.06

    def __init__(self):
        self.input = InputIO()
        self.error = ErrorIO()

    @classmethod
    def sleep(cls):
        """Sleep."""
        sleep(cls.SLEEP_TIME)

    @classmethod
    def snap(cls):
        """Snap."""
        sleep(cls.SNAP_TIME)

    def line(self):
        """Draw a split line."""
        print(self.LINE)
        self.sleep()

    def double_line(self):
        """Draw a double split line."""
        print(self.DOUBLE_LINE)
        self.sleep()

    def newline(self):
        """Print a new line."""
        print("")
        self.sleep()

    @info
    def wait_for_client(self):
        """Please wait for the client..."""

    @info
    def connect_to_server(self):
        """Connecting to the server..."""

    @title
    def game_start(self):
        """[Game Start]"""

    @title
    def battle_start(self):
        """[Battle Start]"""

    @info
    def hint(self):
        """help: /h  quit: /q"""

    @info
    def hint_to_restart(self):
        """help: /h  quit: /q  restart: /r"""

    @title
    def help(self, _: int):
        """."""
        lines = helper.MAINPAGE.split("\n")
        length = -(-max(len(x) for x in lines) // 2)
        wave = "～" * length
        print(wave)
        for x in lines:
            self.snap()
            print(x)
        self.snap()
        print(wave)

    @info
    def cannot_restart(self):
        """Cannot restart now."""

    @info
    def settings_recorded(self, ini_path: Path):
        """."""
        print(f"Settings recorded in {ini_path}")

    @info
    def win_battle(self):
        """Battle victory!"""

    @info
    def lose_battle(self):
        """Battle lost!"""

    @title
    def game_over(self):
        """[Game Over]"""

    @info
    def cards_left(self, cards: "CardCounter"):
        """."""
        if cards.is_opponent:
            print(f"    Enemy's cards left : {cards}")
        else:
            print(f"    Your cards left : {cards}")

    @info
    def show_cards(self, cards: "CardCounter", align: bool = True):
        """."""
        if cards.is_opponent:
            print(f"    Enemy's cards : {cards}")
        elif align:
            print(f"    Your cards    : {cards}")
        else:
            print(f"    Your cards : {cards}")

    @info
    def play(self, unit: "Unit", is_opponent: bool = False):
        """."""
        if is_opponent:
            print(f"    Enemy played : {unit.fullname}")
        else:
            print(f"    You played   : {unit.fullname}")

    @title
    def wait_exit(self):
        """[Exit] Waiting for the opponent..."""

    @info
    def communication_terminated(self):
        """Communication terminated successfully."""

    @title
    def opponent_exit(self):
        """[Exit] The opponent terminated the communication."""

    @title
    def wait_restart(self):
        """[Game Restart] Waiting for the opponent..."""

    @title
    def opponent_restart(self):
        """[Game Restart] The opponent restarted the game."""

    @title
    def rount_start(self, num: int, allies: "CardCounter", enemies: "CardCounter"):
        """."""
        print(f"[Round {num}]  {allies}  vs  {enemies}")

    @info
    def both_destroyed(self):
        """Both were destroyed."""

    @info
    def both_return(self):
        """Both returned back."""

    @info
    def defeat(self, unit: "Unit", is_opponent: bool = False):
        """."""
        if is_opponent:
            print(f"    Enemy's {unit.fullname} was defeated.")
        else:
            print(f"    Your {unit.fullname} was defeated.")

    @info
    def capture(self, unit: "Unit", is_opponent: bool = False):
        """."""
        if is_opponent:
            print(f"    You captured Enemy's {unit.fullname}.")
        else:
            print(f"    Enemy captured your {unit.fullname}.")


class InputIO:
    """Input things (by default in English)."""

    @title_input
    def start_as_server(self):
        """[Init] Start the game as a server? (y/n)"""

    @info_input
    def server_port(self):
        """server port (skip to use the last setting):"""

    @info_input
    def server_port_no_skip(self):
        """server port:"""

    @info_input
    def server_ip(self):
        """server ip (skip to use the last setting):"""

    @info_input
    def action(self):
        """>"""


class ErrorIO:
    """Input things (by default in English)."""

    @error
    def server_not_found(self):
        """Server not found."""

    @error
    def no_recorded_setting(self):
        """No recorded setting."""

    @error
    def no_recorded_section(self, section: str):
        """."""
        print(f"[Error] No recorded setting for {section}.")
