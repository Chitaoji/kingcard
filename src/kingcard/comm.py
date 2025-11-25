"""
Contains communicating utils: TcpCommunicator, etc.

NOTE: this module is private. All functions and objects are available in the main
`kingcard` namespace - use that instead.

"""

from configparser import ConfigParser
from pathlib import Path
from socket import AF_INET, SOCK_STREAM, socket

from .error import BattleRestart, CommunicationError, GameQuit
from .io import IO

__all__ = ["TcpCommunicator"]


class Communicator:
    """Communicate with the opponent."""

    def __init__(self, io: IO) -> None:
        self.io = io

    def send(self, message: str) -> None:
        """Send messages."""

    def recv(self) -> str:
        """Receive messages."""
        return ""

    def recv_only(self) -> str:
        """Receive messages only."""
        return ""

    def close(self) -> None:
        """Close the communicator."""

    def _check_for_command(self, msg: str) -> None:
        if not msg.startswith("/"):
            return
        match msg[1:]:
            case "q":
                self.io.double_line()
                self.io.opponent_exit()
                self.close()
                raise GameQuit()
            case "r":
                self.io.double_line()
                self.io.opponent_restart()
                raise BattleRestart()
        raise CommunicationError()


class TcpCommunicator(Communicator):
    """Communicate with the opponent."""

    def __init__(self, io: IO) -> None:
        super().__init__(io)
        self.datadir = Path("~/AppData/Local/KingCard").expanduser()

        io.start_as_server()
        self.is_server = io.input.yes_or_no()

        if self.is_server:
            ip = ""
            io.server_port()
            port = io.input.input()
            if not port:
                ip, port = self.load_settings()
            else:
                self.save_settings(ip, port)
        else:
            io.server_ip()
            ip = io.input.input()
            if not ip:
                ip, port = self.load_settings()
            else:
                io.server_port()
                port = io.input.input()
                if not port:
                    _, port = self.load_settings()
                self.save_settings(ip, port)

        tcp_socket = socket(AF_INET, SOCK_STREAM)
        test_msg = "KingCard Game-Start"

        if self.is_server:
            tcp_socket.bind((ip, int(port)))
            tcp_socket.listen(128)
            io.wait_for_client()
            self.tcp_socket, _ = tcp_socket.accept()
            self.tcp_socket.send(test_msg.encode("utf-8"))
        else:
            tcp_socket.connect((ip, int(port)))
            self.tcp_socket = tcp_socket
            io.connect_to_server()
            if not self.tcp_socket.recv(1024).decode("utf-8") == test_msg:
                io.error.server_not_found()
                raise CommunicationError()

    def save_settings(self, ip: str, port: str) -> None:
        """Save the settings."""
        if not self.datadir.exists():
            self.datadir.mkdir(parents=True)

        parser = ConfigParser()
        section = "server" if self.is_server else "client"

        if not (ini_path := self.datadir / "settings.ini").exists():
            dct = {section: {"port": port}}
            if not self.is_server:
                dct[section]["ip"] = ip
            parser.read_dict(dct)
        else:
            parser.read(ini_path, encoding="utf-8")
            if not parser.has_section(section):
                parser.add_section(section)
            if not self.is_server:
                parser.set(section, "ip", ip)
            parser.set(section, "port", port)

        with open(ini_path, "w", encoding="utf-8") as f:
            parser.write(f)

        self.io.settings_recorded(ini_path)

    def load_settings(self) -> tuple[str, str]:
        """Load the settings."""
        if not self.datadir.exists():
            self.datadir.mkdir(parents=True)

        if not (ini_path := self.datadir / "settings.ini").exists():
            self.io.error.no_recorded_setting()
            raise GameQuit()

        parser = ConfigParser()
        parser.read(ini_path, encoding="utf-8")

        section = "server" if self.is_server else "client"
        if not parser.has_section(section):
            self.io.error.no_recorded_section(section)
            raise GameQuit()

        if self.is_server:
            ip = ""
        else:
            ip = parser.get(section, "ip")
        port = parser.get(section, "port")
        return ip, port

    def send(self, message: str) -> None:
        return self.tcp_socket.send(message.encode("utf-8"))

    def recv(self) -> str:
        msg = self.tcp_socket.recv(1024).decode("utf-8")
        self._check_for_command(msg)
        return msg

    def recv_only(self) -> str:
        return self.tcp_socket.recv(1024).decode("utf-8")

    def close(self) -> None:
        self.tcp_socket.close()
