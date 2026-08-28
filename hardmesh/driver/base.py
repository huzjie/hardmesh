"""设备驱动基类：统一 read/write/act 接口。"""
from typing import Any, Optional


class Driver:
    """所有设备驱动的基类。子类实现底层通信。"""

    name = "base"

    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}

    def connect(self, device_id: str) -> None:
        """建立与设备的连接。"""

    def disconnect(self, device_id: str) -> None:
        """断开连接。"""

    def read(self, device_id: str, channel: Optional[str] = None) -> Any:
        raise NotImplementedError

    def write(self, device_id: str, channel: str, value: Any) -> Any:
        raise NotImplementedError

    def act(self, device_id: str, action: str, params: dict) -> Any:
        raise NotImplementedError

    def stream(self, device_id: str, channel: Optional[str] = None):
        """持续数据流生成器（可选）。"""
        yield from ()
