"""设备注册中心：集中登记、查询、订阅设备。"""
import threading
from typing import Any, Dict, List, Optional

from hardmesh.device.base import Device
from hardmesh.device.descriptor import DeviceDescriptor
from hardmesh.errors import DeviceNotFound


class DeviceRegistry:
    """线程安全的设备注册中心。"""

    def __init__(self):
        self._devices: Dict[str, Device] = {}
        self._lock = threading.RLock()
        self._listeners: List[Any] = []

    def register(self, device: Device) -> Device:
        with self._lock:
            self._devices[device.device_id] = device
            self._notify("register", device.device_id)
        return device

    def register_descriptor(self, descriptor: DeviceDescriptor, driver=None) -> Device:
        return self.register(Device(descriptor=descriptor, driver=driver))

    def unregister(self, device_id: str) -> Optional[Device]:
        with self._lock:
            dev = self._devices.pop(device_id, None)
            if dev:
                self._notify("unregister", device_id)
            return dev

    def get(self, device_id: str) -> Device:
        with self._lock:
            dev = self._devices.get(device_id)
            if dev is None:
                raise DeviceNotFound(f"设备 {device_id} 未注册")
            return dev

    def list(self) -> List[Device]:
        with self._lock:
            return list(self._devices.values())

    def ids(self) -> List[str]:
        with self._lock:
            return list(self._devices.keys())

    def filter(self, kind: Optional[str] = None, capability: Optional[str] = None,
               state: Optional[str] = None) -> List[Device]:
        out = []
        with self._lock:
            for d in self._devices.values():
                if kind and d.descriptor.kind != kind:
                    continue
                if capability and not d.supports(capability):
                    continue
                if state and d.state.value != state:
                    continue
                out.append(d)
        return out

    def subscribe(self, listener) -> None:
        with self._lock:
            self._listeners.append(listener)

    def _notify(self, event: str, device_id: str) -> None:
        for l in list(self._listeners):
            try:
                l(event, device_id)
            except Exception:
                pass

    def snapshot(self) -> List[Dict[str, Any]]:
        return [d.snapshot() for d in self.list()]
