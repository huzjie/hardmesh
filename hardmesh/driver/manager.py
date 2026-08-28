"""驱动管理器：按名称解析并缓存驱动实例。"""
from typing import Dict, Optional

from hardmesh.driver.base import Driver


class DriverManager:
    """管理驱动实例，支持注册自定义驱动。"""

    def __init__(self):
        self._drivers: Dict[str, Driver] = {}
        self._classes: Dict[str, type] = {}

    def register_class(self, name: str, cls: type) -> None:
        self._classes[name] = cls

    def resolve(self, name: str, config: Optional[dict] = None) -> Driver:
        if name in self._drivers:
            return self._drivers[name]
        if name in self._classes:
            drv = self._classes[name](config)
            self._drivers[name] = drv
            return drv
        # 回退到 mock，保证离线可用
        from hardmesh.driver.mock import MockDriver
        drv = MockDriver(config)
        self._drivers[name] = drv
        return drv

    def get(self, name: str) -> Optional[Driver]:
        return self._drivers.get(name)

    def names(self) -> list:
        return sorted(set(list(self._drivers.keys()) + list(self._classes.keys())))
