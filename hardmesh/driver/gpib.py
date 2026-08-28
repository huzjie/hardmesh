"""GPIB/VISA 仪器驱动：面向示波器/信号源等实验室仪器（可选依赖 pyvisa）。"""
from typing import Any, Optional

from hardmesh.driver.base import Driver
from hardmesh.errors import DriverError


class GpibDriver(Driver):
    name = "gpib"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self.address = self.config.get("address", "GPIB0::1::INSTR")
        self._inst = None

    def connect(self, device_id: str) -> None:
        try:
            import pyvisa  # noqa: WPS433
        except ImportError as e:
            raise DriverError("使用 GPIB 驱动需安装 pyvisa: pip install pyvisa pyvisa-py") from e
        rm = pyvisa.ResourceManager()
        self._inst = rm.open_resource(self.address)

    def disconnect(self, device_id: str) -> None:
        if self._inst:
            self._inst.close()
            self._inst = None

    def read(self, device_id: str, channel: Optional[str] = None) -> Any:
        if self._inst is None:
            raise DriverError("GPIB 未连接")
        return self._inst.query("*IDN?").strip()

    def write(self, device_id: str, channel: str, value: Any) -> Any:
        if self._inst is None:
            raise DriverError("GPIB 未连接")
        self._inst.write(f"{channel} {value}")
        return {"ack": True}

    def act(self, device_id: str, action: str, params: dict) -> Any:
        return self.write(device_id, action, params)
