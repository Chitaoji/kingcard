"""
Contains communicating utils: TcpCommunicator, etc.

NOTE: this module is private. All functions and objects are available in the main
`kingcard` namespace - use that instead.

"""

from configparser import ConfigParser
from pathlib import Path
from socket import AF_INET, SOCK_STREAM, socket

from .error import CommunicationError, GameQuit
from .io import IO

__all__ = ["TcpCommunicator"]


class Communicator:
    """Communicate with the opponent."""

    def send(self, message: str) -> None:
        """Send messages."""

    def recv(self) -> str:
        """Receive messages."""

    def close(self) -> None:
        """Close the communicator."""


class TcpCommunicator(Communicator):
    """Communicate with the opponent."""

    def __init__(self, io: IO) -> None:
        self.datadir = Path("~/AppData/Local/KingCard").expanduser()
        self.io = io

        match io.input.start_as_server():
            case "y":
                self.is_server = True
            case "n":
                self.is_server = False
            case _:
                raise ValueError("please type y/n")

        if self.is_server:
            ip = ""
            port = io.input.server_port()
            if not port:
                ip, port = self.load_settings()
            else:
                self.save_settings(ip, port)
        else:
            ip = io.input.server_ip()
            if not ip:
                ip, port = self.load_settings()
            else:
                port = io.input.server_port_no_skip()
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
        """Send messages."""
        return self.tcp_socket.send(message.encode("utf-8"))

    def recv(self) -> str:
        """Receive messages."""
        return self.tcp_socket.recv(1024).decode("utf-8")

    def close(self) -> None:
        """Close the communicator."""
        self.tcp_socket.close()
