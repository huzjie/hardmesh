"""设备基类：统一设备行为模型。"""
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from hardmesh.device.capability import Capability
from hardmesh.device.descriptor import DeviceDescriptor
from hardmesh.device.state import DeviceState, can_transition
from hardmesh.errors import CapabilityDenied, DeviceOffline


DeviceCapability = Capability
DeviceAction = str


@dataclass
class Device:
    """运行时设备实例：持有描述符 + 状态 + 驱动。"""
    descriptor: DeviceDescriptor
    state: DeviceState = DeviceState.REGISTERED
    driver: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_seen: float = field(default_factory=time.time)
    _lock: threading.RLock = field(default_factory=threading.RLock, repr=False)

    @property
    def device_id(self) -> str:
        return self.descriptor.device_id

    @property
    def name(self) -> str:
        return self.descriptor.name

    def supports(self, capability: str) -> bool:
        return capability in self.descriptor.capabilities

    def require_capability(self, capability: str) -> None:
        if not self.supports(capability):
            raise CapabilityDenied(
                f"设备 {self.device_id} 不支持能力 {capability}，已声明: {self.descriptor.capabilities}"
            )

    def require_online(self) -> None:
        if not self.state.online:
            raise DeviceOffline(f"设备 {self.device_id} 处于 {self.state.value} 状态，无法操作")

    def transition(self, dst: DeviceState) -> bool:
        with self._lock:
            if not can_transition(self.state, dst):
                return False
            self.state = dst
            self.last_seen = time.time()
            return True

    def read(self, channel: Optional[str] = None) -> Any:
        self.require_capability(Capability.READ.value)
        self.require_online()
        if self.driver is None:
            return None
        return self.driver.read(self.device_id, channel)

    def write(self, channel: str, value: Any) -> Any:
        self.require_capability(Capability.WRITE.value)
        self.require_online()
        if self.driver is None:
            return value
        return self.driver.write(self.device_id, channel, value)

    def act(self, action: str, **params: Any) -> Any:
        self.require_online()
        spec = self.descriptor.action_by_name(action)
        if spec is None:
            raise CapabilityDenied(f"设备 {self.device_id} 无动作 {action}")
        self.require_capability(spec.capability)
        validated = {p.name: p.validate(params.get(p.name)) for p in spec.parameters}
        if self.driver is None:
            return {"action": action, "params": validated, "result": "noop"}
        return self.driver.act(self.device_id, action, validated)

    def snapshot(self) -> Dict[str, Any]:
        return {
            "device_id": self.device_id,
            "name": self.name,
            "kind": self.descriptor.kind,
            "state": self.state.value,
            "capabilities": self.descriptor.capabilities,
            "driver": self.descriptor.driver,
            "last_seen": self.last_seen,
        }
