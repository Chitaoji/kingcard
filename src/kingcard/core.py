"""
Contains the core of kingcard: KingCardSimulator, etc.

NOTE: this module is private. All functions and objects are available in the main
`kingcard` namespace - use that instead.

"""

from configparser import ConfigParser
from pathlib import Path
from socket import AF_INET, SOCK_STREAM, socket
from time import sleep

from .arms import ARMS
from .counter import UnitsCounter
from .error import CommunicationEnd, CommunicationError, CommunicationRestart, GameOver

__all__ = ["KingCardSimulator"]

SLEEP_TIME = 1

SPLIT1 = "-" * 50 + "\n"
SPLIT2 = "=" * 50 + "\n"


class KingCardSimulator:
    """Simulator of the King-Card game."""

    def __init__(self) -> None:
        """Initialize."""
        self.datadir = Path("~/AppData/Local/KingCard").expanduser()
        self.round = 0
        self.locked = False

        match input("[Init] Start the game as a server? (y/n) ").lower():
            case "y":
                self.is_server = True
            case "n":
                self.is_server = False
            case _:
                raise ValueError("please type y/n")

        if self.is_server:
            self.ip = ""
            port = input("    server port (skip to use the last setting): ")
            if not port:
                self.load_settings()
            else:
                self.port = int(port)
                self.save_settings()
        else:
            self.ip = input("    server ip (skip to use the last setting): ")
            if not self.ip:
                self.load_settings()
            else:
                self.port = int(input("server port: "))
                self.save_settings()

        tcp_socket = socket(AF_INET, SOCK_STREAM)
        test_msg = "D-Card Game Start"

        if self.is_server:
            tcp_socket.bind((self.ip, self.port))
            tcp_socket.listen(128)
            print("    Please wait for the client...")
            self.tcp_socket, _ = tcp_socket.accept()
            self.tcp_socket.send(test_msg.encode("utf-8"))
        else:
            tcp_socket.connect((self.ip, self.port))
            self.tcp_socket = tcp_socket
            print("    Connecting to the server...")
            self.sleep()
            if not self.tcp_socket.recv(1024).decode("utf-8") == test_msg:
                print("[Error] Server not found.")
                raise CommunicationError()

        self.units = UnitsCounter()
        self.enemies = UnitsCounter()

        print(f"{SPLIT2}[Game Start]\n    help: /h  quit: /q  restart: /r")
        self.sleep()

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

    def sleep(self) -> None:
        """Sleep."""
        sleep(SLEEP_TIME)

    def lock(self) -> None:
        """Lock the status."""
        self.locked = True

    def loop(self) -> None:
        """Loop until the communcation is ended."""
        while True:
            try:
                self.next_round()
            except CommunicationEnd:
                break
            except CommunicationRestart:
                self.round = 0
            except GameOver as e:
                self.sleep()
                match e.args[0]:
                    case "win":
                        print(f"{SPLIT1}    Your've won the game!")
                    case "lose":
                        print(f"{SPLIT1}    Your've losed the game!")
                self.sleep()
                print(f"\n    Your cards left   : {self.units}")
                self.sleep()
                print(f"    Enemy's cards left: {self.enemies}")
                self.sleep()
                self.round = -1

    def next_round(self) -> None:
        """Communicate with server/client."""
        if self.locked:
            self.locked = False
            msg = input("    > ")
        elif self.round == -1:
            msg = input(
                f"{SPLIT1}[Game Over]\n    help: /h  quit: /q  restart: /r\n    > "
            )
        else:
            self.round += 1
            if self.round == 1:
                print(
                    f"{SPLIT1}    Your cards   : {self.units}\n"
                    f"    Enemy's cards: {self.enemies}"
                )
                self.sleep()
            msg = input(
                f"{SPLIT1}[Round {self.round}] {self.units}  vs  {self.enemies}\n"
                "    > "
            )
        self._check_message(msg)

    def _check_message(self, message: str) -> None:
        if not message.startswith("/"):
            if self.round == -1:
                self.lock()
                return
            if not message:
                self.lock()
                return
            for unit in ARMS.values():
                if unit.match(message):
                    print(f"    You played: {unit.fullname}")
                    self.sleep()
                    self.tcp_socket.send(unit.tag.encode("utf-8"))
                    enemy = ARMS[self._get_message_from_opponent()]
                    print(f"    Enemy played: {enemy.fullname}")
                    self.sleep()
                    unit.on_round_begin(enemy, self.units, self.enemies)
                    self.sleep()
                    return
            self.lock()

        match message[1:].lower():
            case "q":
                self.tcp_socket.send(message.encode("utf-8"))
                print(f"{SPLIT2}[Exit] Waiting for the opponent...")
                self.tcp_socket.recv(1024)
                print("    Communication terminated successfully.")
                self.tcp_socket.close()
                raise CommunicationEnd()
            case "r":
                self.tcp_socket.send(message.encode("utf-8"))
                print(f"{SPLIT2}[Game Restart] Waiting for the opponent...")
                self.sleep()
                self.tcp_socket.recv(1024)
                raise CommunicationRestart()

    def _get_message_from_opponent(self) -> str:
        msg = self.tcp_socket.recv(1024).decode("utf-8")
        if not msg.startswith("/"):
            return msg
        match msg[1:].lower():
            case "q":
                print(f"{SPLIT2}[Exit] The opponent terminated the communication.")
                self.tcp_socket.close()
                raise CommunicationEnd()
            case "r":
                print(f"{SPLIT2}[Game Restart] The opponent has restarted the game.")
                self.sleep()
                raise CommunicationRestart()
