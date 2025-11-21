"""
Contains the core of kingcard: KingCardSimulator, etc.

NOTE: this module is private. All functions and objects are available in the main
`kingcard` namespace - use that instead.

"""

from configparser import ConfigParser
from pathlib import Path
from socket import AF_INET, SOCK_STREAM, socket

from .arms import ARMS, set_unit_io
from .counter import CardCounter
from .error import CommunicationEnd, CommunicationError, CommunicationRestart, GameOver
from .io import IO

__all__ = ["KingCardSimulator"]


SPLIT1 = "-" * 50 + "\n"
SPLIT2 = "=" * 50 + "\n"


class KingCardSimulator:
    """Simulator of the King-Card game."""

    def __init__(self) -> None:
        """Initialize."""
        self.datadir = Path("~/AppData/Local/KingCard").expanduser()
        self.round = 0
        self.locked = False

        self.io = IO()

        match self.io.input.start_as_server():
            case "y":
                self.is_server = True
            case "n":
                self.is_server = False
            case _:
                raise ValueError("please type y/n")

        if self.is_server:
            self.ip = ""
            port = self.io.input.server_port()
            if not port:
                self.load_settings()
            else:
                self.port = int(port)
                self.save_settings()
        else:
            self.ip = self.io.input.server_ip()
            if not self.ip:
                self.load_settings()
            else:
                self.port = int(self.io.input.server_port_no_skip())
                self.save_settings()

        tcp_socket = socket(AF_INET, SOCK_STREAM)
        test_msg = "KingCard Game-Start"

        if self.is_server:
            tcp_socket.bind((self.ip, self.port))
            tcp_socket.listen(128)
            self.io.wait_for_client()
            self.tcp_socket, _ = tcp_socket.accept()
            self.tcp_socket.send(test_msg.encode("utf-8"))
        else:
            tcp_socket.connect((self.ip, self.port))
            self.tcp_socket = tcp_socket
            self.io.connect_to_server()
            if not self.tcp_socket.recv(1024).decode("utf-8") == test_msg:
                self.io.error.server_not_found()
                raise CommunicationError()

        self.ours = CardCounter()
        self.enemies = CardCounter(None, True)

        set_unit_io(self.io)

        self.io.double_line()
        self.io.game_start()
        self.io.hint()

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

        self.io.settings_recorded(ini_path)

    def load_settings(self) -> None:
        """Load the settings."""
        if not self.datadir.exists():
            self.datadir.mkdir(parents=True)

        if not (ini_path := self.datadir / "settings.ini").exists():
            self.io.error.no_recorded_setting()
            raise CommunicationEnd()

        parser = ConfigParser()
        parser.read(ini_path, encoding="utf-8")

        section = "server" if self.is_server else "client"
        if not parser.has_section(section):
            self.io.error.no_recorded_section(section)
            raise CommunicationEnd()

        if self.is_server:
            self.ip = ""
        else:
            self.ip = parser.get(section, "ip")
        self.port = int(parser.get(section, "port"))

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
                match e.args[0]:
                    case "win":
                        self.io.line()
                        self.io.game_win()
                    case "lose":
                        self.io.line()
                        self.io.game_lose()
                    case _:
                        raise e
                self.io.newline()
                self.io.cards_left(self.ours)
                self.round = -1

    def next_round(self) -> None:
        """Communicate with server/client."""
        if self.locked:
            self.locked = False
            msg = self.io.input.action()
        elif self.round == -1:
            self.io.line()
            self.io.game_over()
            self.io.hint_restart()
            msg = self.io.input.action()
        else:
            self.round += 1
            if self.round == 1:
                self.io.line()
                self.io.cards(self.ours)
                self.io.cards(self.enemies)
            self.io.line()
            self.io.rount_start(self.round, self.ours, self.enemies)
            msg = self.io.input.action()
        self._check_message(msg)

    def _check_message(self, message: str) -> None:
        if not message.startswith("/"):
            if self.round == -1 or not message:
                self.lock()
                return
            for tag, n in self.ours.units.items():
                if n <= 0:
                    continue
                unit = ARMS[tag]
                if unit.match(message):
                    self.io.played(unit)
                    self.tcp_socket.send(unit.tag.encode("utf-8"))
                    enemy = ARMS[self._get_message_from_opponent()]
                    self.io.played(enemy, is_opponent=True)
                    unit.on_round_begin(enemy, self.ours, self.enemies)
                    return
            self.lock()
            return

        match message[1:].lower():
            case "q":
                self.tcp_socket.send(message.encode("utf-8"))
                self.io.double_line()
                self.io.wait_exit()
                self.tcp_socket.recv(1024)
                self.io.communication_terminated()
                self.tcp_socket.close()
                raise CommunicationEnd()
            case "r":
                self.tcp_socket.send(message.encode("utf-8"))
                self.io.double_line()
                self.io.wait_restart()
                self.tcp_socket.recv(1024)
                raise CommunicationRestart()
            case "h":
                self.io.help(1)
                self.lock()

    def _get_message_from_opponent(self) -> str:
        msg = self.tcp_socket.recv(1024).decode("utf-8")
        if not msg.startswith("/"):
            return msg
        match msg[1:].lower():
            case "q":
                self.io.double_line()
                self.io.opponent_exit()
                self.tcp_socket.close()
                raise CommunicationEnd()
            case "r":
                self.io.double_line()
                self.io.opponent_restart()
                raise CommunicationRestart()
