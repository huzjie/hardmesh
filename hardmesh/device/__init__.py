"""设备抽象层。"""
from hardmesh.device.base import Device, DeviceState, DeviceCapability, DeviceAction  # noqa: F401
from hardmesh.device.capability import Capability  # noqa: F401
from hardmesh.device.descriptor import DeviceDescriptor, ActionSpec, ParameterSpec  # noqa: F401
from hardmesh.device.registry import DeviceRegistry  # noqa: F401

__all__ = [
    "Device", "DeviceState", "DeviceCapability", "DeviceAction",
    "Capability", "DeviceDescriptor", "ActionSpec", "ParameterSpec",
    "DeviceRegistry",
]
