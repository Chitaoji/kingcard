"""
Contains the core of kingcard: KingCardSimulator, etc.

NOTE: this module is private. All functions and objects are available in the main
`kingcard` namespace - use that instead.

"""

from configparser import ConfigParser
from pathlib import Path
from socket import AF_INET, SOCK_STREAM, socket

from .counter import UnitsCounter

__all__ = ["KingCardSimulator"]


class KingCardSimulator:
    """Simulator of the King-Card game."""

    def __init__(self) -> None:
        """Initialize."""
        self.datadir = Path("~/AppData/Local/KingCard").expanduser()
        self.round = -1

        match input("[Init] Start the game as a server? (y/n) ").lower():
            case "y":
                self.is_server = True
            case "n":
                self.is_server = False
            case _:
                raise ValueError("please type y/n")

        match input("[Init] Load the recorded settings? (y/n) ").lower():
            case "y":
                self.load_settings()
            case "n":
                self.ip = "" if self.is_server else input("server ip: ")
                self.port = int(input("server port: "))
                self.save_settings()
            case _:
                raise ValueError("please type y/n")

        tcp_socket = socket(AF_INET, SOCK_STREAM)
        test_msg = "D-Card Game Start"

        if self.is_server:
            tcp_socket.bind((self.ip, self.port))
            tcp_socket.listen(128)
            print("Please wait for the client...")
            self.tcp_socket, _ = tcp_socket.accept()
            self.tcp_socket.send(test_msg.encode("utf-8"))
        else:
            tcp_socket.connect((self.ip, self.port))
            self.tcp_socket = tcp_socket
            print("Connecting to the server...")
            if not self.tcp_socket.recv(1024).decode("utf-8") == test_msg:
                print("[Error] Server not found.")
                raise CommunicationError()

        self.my_units = UnitsCounter()
        self.opp_units = UnitsCounter()

        print("[Game Start] help: /h  quit: /q")

    def loop(self) -> None:
        """Loop until the communcation is ended."""
        while True:
            try:
                self.communicate()
            except CommunicationEnd:
                break
            except CommunicationRestart:
                self.round = 0
            except GameOver:
                self.round = -1

    def communicate(self) -> None:
        """Communicate with server/client."""
        if self.round == -1:
            msg = input("[Game Over] restart: /r  help: /h  quit: /q ")
            self._check_message(msg)
            return
        self.round += 1
        msg = input(
            f"[Round {self.round}] {self.my_units}  vs  {self.opp_units}\n"
            "Play your card: "
        )
        self._check_message(msg)

    def save_settings(self) -> None:
        """Save the settings."""
        if not self.datadir.exists():
            self.datadir.mkdir(parents=True)

        parser = ConfigParser()
        section = "server" if self.is_server else "client"

        if not (ini_path := self.datadir / "settings.ini").exists():
            dct = {section: {"port": self.port}}
            if not self.is_server:
                dct[section]["ip"] = self.ip
            parser.read_dict(dct)
        else:
            parser.read(ini_path, encoding="utf-8")
            if not parser.has_section(section):
                parser.add_section(section)
            if not self.is_server:
                parser.set(section, "ip", self.ip)
            parser.set(section, "port", str(self.port))

        with open(ini_path, "w", encoding="utf-8") as f:
            parser.write(f)

        print(f"Settings recorded in {ini_path}")

    def load_settings(self) -> None:
        """Load the settings."""
        if not self.datadir.exists():
            self.datadir.mkdir(parents=True)

        if not (ini_path := self.datadir / "settings.ini").exists():
            print("[Error] No recorded setting.")
            raise CommunicationEnd()

        parser = ConfigParser()
        parser.read(ini_path, encoding="utf-8")

        section = "server" if self.is_server else "client"
        if not parser.has_section(section):
            print(f"[Error] No recorded setting for {section}.")
            raise CommunicationEnd()

        if self.is_server:
            self.ip = ""
        else:
            self.ip = parser.get(section, "ip")
        self.port = int(parser.get(section, "port"))

    def _check_message(self, message: str) -> None:
        if not message.startswith("/"):
            if self.round > -1:
                self.tcp_socket.send(message.encode("utf-8"))
                print(f"The opponent played: {self._get_message_from_opponent()}")
            return
        match message[1:].lower():
            case "q":
                self.tcp_socket.send(message.encode("utf-8"))
                print("[Exit] Waiting for the opponent...")
                self.tcp_socket.recv(1024)
                print("[Exit] Communication terminated.")
                self.tcp_socket.close()
                raise CommunicationEnd()
            case "r":
                self.tcp_socket.send(message.encode("utf-8"))
                print("[Game Restart] Waiting for the opponent...")
                self.tcp_socket.recv(1024)
                raise CommunicationRestart()

    def _get_message_from_opponent(self) -> str:
        msg = self.tcp_socket.recv(1024).decode("utf-8")
        if not msg.startswith("/"):
            return msg
        match msg[1:].lower():
            case "q":
                print("[Exit] The opponent terminated the communication.")
                self.tcp_socket.close()
                raise CommunicationEnd()
            case "r":
                print("[Game Restart] The opponent restarted the game.")
                raise CommunicationRestart()


class CommunicationError(Exception):
    """Communication Error."""


class CommunicationEnd(Exception):
    """Communication End."""


class CommunicationRestart(Exception):
    """Communication Restart."""


class GameOver(Exception):
    """Game over."""
