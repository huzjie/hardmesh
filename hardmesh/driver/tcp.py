"""TCP 网络设备驱动：面向通过 TCP socket 暴露命令协议的设备。"""
import socket
from typing import Any, Optional

from hardmesh.driver.base import Driver
from hardmesh.errors import DriverError


class TcpDriver(Driver):
    name = "tcp"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self.host = self.config.get("host", "127.0.0.1")
        self.port = int(self.config.get("port", 5000))
        self.timeout = float(self.config.get("timeout", 3.0))
        self._sock = None

    def connect(self, device_id: str) -> None:
        try:
            self._sock = socket.create_connection((self.host, self.port), timeout=self.timeout)
        except OSError as e:
            raise DriverError(f"TCP 连接失败 {self.host}:{self.port}: {e}")

    def disconnect(self, device_id: str) -> None:
        if self._sock:
            try:
                self._sock.close()
            except OSError:
                pass
            self._sock = None

    def _send(self, payload: str) -> str:
        if self._sock is None:
            raise DriverError("TCP 未连接")
        self._sock.sendall((payload + "\n").encode("utf-8"))
        data = b""
        while not data.endswith(b"\n"):
            chunk = self._sock.recv(1024)
            if not chunk:
                break
            data += chunk
        return data.decode("utf-8").strip()

    def read(self, device_id: str, channel: Optional[str] = None) -> Any:
        return self._send(f"READ {channel or 'value'}")

    def write(self, device_id: str, channel: str, value: Any) -> Any:
        return self._send(f"WRITE {channel} {value}")

    def act(self, device_id: str, action: str, params: dict) -> Any:
        return self._send(f"ACT {action} {params}")
