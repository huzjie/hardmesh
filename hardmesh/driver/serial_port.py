"""串口设备驱动：面向 RS-232/RS-485 仪器（可选依赖 pyserial）。

未安装 pyserial 时仅登记驱动类，实际连接会抛出明确错误，
避免影响内核零依赖启动。
"""
from typing import Any, Optional

from hardmesh.driver.base import Driver
from hardmesh.errors import DriverError


class SerialDriver(Driver):
    name = "serial"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self.port = self.config.get("port", "COM1")
        self.baudrate = int(self.config.get("baudrate", 9600))
        self._ser = None

    def connect(self, device_id: str) -> None:
        try:
            import serial  # noqa: WPS433
        except ImportError as e:
            raise DriverError("使用串口驱动需安装 pyserial: pip install pyserial") from e
        self._ser = serial.Serial(self.port, self.baudrate, timeout=1)

    def disconnect(self, device_id: str) -> None:
        if self._ser:
            self._ser.close()
            self._ser = None

    def read(self, device_id: str, channel: Optional[str] = None) -> Any:
        if self._ser is None:
            raise DriverError("串口未连接")
        return self._ser.readline().decode("utf-8", "ignore").strip()

    def write(self, device_id: str, channel: str, value: Any) -> Any:
        if self._ser is None:
            raise DriverError("串口未连接")
        self._ser.write((f"{channel}={value}\n").encode("utf-8"))
        return {"ack": True}

    def act(self, device_id: str, action: str, params: dict) -> Any:
        return self.write(device_id, action, params)
