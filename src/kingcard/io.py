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
    from .cards import Card
    from .counter import CardCounter


__all__ = []


T = TypeVar("T")
U = TypeVar("U")


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


def receive(method: Callable[[T], None]) -> Callable[[T], str]:
    """Receive the input."""

    def wrapper(*args):
        msg = input("    " + method.__doc__ + " ").lower()
        if msg.startswith("/"):
            io: "InputIO" = args[0]
            io.command_behaviour(msg)
            return wrapper(*args)
        return msg

    return wrapper


def require(
    items: dict[str, U],
) -> Callable[[Callable[[T], None]], Callable[[T], U]]:
    """Require certain input."""

    def decorator(method: Callable[[T], None]) -> Callable[[T], U]:
        def wrapper(*args) -> U:
            msg = input("    " + method.__doc__ + " ").lower()
            if msg.startswith("/"):
                io: "InputIO" = args[0]
                io.command_behaviour(msg)
            elif msg in items:
                return items[msg]
            return wrapper(*args)

        return wrapper

    return decorator


def require_card(method: Callable[[T], None]) -> Callable[[T], U]:
    """Require a card."""

    def wrapper(*args) -> U:
        items: dict[str, "Card"] = args[-1]
        msg = input("    " + method.__doc__ + " ").lower()
        if msg.startswith("/"):
            io: "InputIO" = args[0]
            io.command_behaviour(msg)
        else:
            for unit in items.values():
                if unit.match(msg):
                    return unit
        return wrapper(*args)

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
        """[KingCard Game Start]"""

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
    def battle_over(self):
        """[Battle Over]"""

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
    def play(self, card: "Card", is_opponent: bool = False):
        """."""
        if is_opponent:
            print(f"    Enemy played : {card.fullname}")
        else:
            print(f"    You played   : {card.fullname}")

    @title
    def wait_exit(self):
        """[Exit] Waiting..."""

    @info
    def communication_terminated(self):
        """Communication terminated successfully."""

    @title
    def opponent_exit(self):
        """[Exit] The opponent terminated the communication."""

    @title
    def wait_restart(self):
        """[Battle Restart] Waiting for the opponent..."""

    @title
    def opponent_restart(self):
        """[Battle Restart] The opponent restarted the game."""

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
    def defeat(self, unit: "Card", is_opponent: bool = False):
        """."""
        if is_opponent:
            print(f"    Enemy's {unit.fullname} was defeated.")
        else:
            print(f"    Your {unit.fullname} was defeated.")

    @info
    def capture(self, unit: "Card", is_opponent: bool = False):
        """."""
        if is_opponent:
            print(f"    You captured Enemy's {unit.fullname}.")
        else:
            print(f"    Enemy captured your {unit.fullname}.")

    @title
    def start_as_server(self):
        """[Init] Start the game as a server? (y/n)"""

    @title
    def server_ip(self):
        """server ip (skip to use the last setting):"""

    @title
    def server_port(self):
        """server port (skip to use the last setting):"""


class InputIO:
    """Input things (by default in English)."""

    @receive
    def input(self):
        """>"""

    @require({"y": True, "n": False})
    def yes_or_no(self):
        """>"""

    @require_card
    def card(self, items: dict[str, "Card"], /):
        """>"""

    @require({"": None})
    def command(self, items: dict[str, "Card"], /):
        """>"""

    @staticmethod
    def command_behaviour(message: str) -> None:
        """Needs to bind."""


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
