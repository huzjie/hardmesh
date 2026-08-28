"""设备状态机定义。"""
from enum import Enum


class DeviceState(str, Enum):
    """设备生命周期状态。"""
    UNREGISTERED = "unregistered"
    REGISTERED = "registered"
    CONNECTING = "connecting"
    IDLE = "idle"               # 在线空闲
    BUSY = "busy"               # 正在执行
    CALIBRATING = "calibrating"
    FAULT = "fault"             # 故障
    EMERGENCY_STOP = "estop"    # 急停
    OFFLINE = "offline"

    @property
    def online(self) -> bool:
        return self in (DeviceState.IDLE, DeviceState.BUSY, DeviceState.CALIBRATING)

    @property
    def terminal(self) -> bool:
        return self in (DeviceState.FAULT, DeviceState.EMERGENCY_STOP)


_VALID_TRANSITIONS = {
    DeviceState.UNREGISTERED: {DeviceState.REGISTERED},
    DeviceState.REGISTERED: {DeviceState.CONNECTING, DeviceState.OFFLINE},
    DeviceState.CONNECTING: {DeviceState.IDLE, DeviceState.FAULT},
    DeviceState.IDLE: {DeviceState.BUSY, DeviceState.CALIBRATING, DeviceState.OFFLINE, DeviceState.EMERGENCY_STOP},
    DeviceState.BUSY: {DeviceState.IDLE, DeviceState.FAULT, DeviceState.EMERGENCY_STOP},
    DeviceState.CALIBRATING: {DeviceState.IDLE, DeviceState.FAULT, DeviceState.EMERGENCY_STOP},
    DeviceState.FAULT: {DeviceState.OFFLINE, DeviceState.REGISTERED},
    DeviceState.EMERGENCY_STOP: {DeviceState.REGISTERED, DeviceState.OFFLINE},
    DeviceState.OFFLINE: {DeviceState.REGISTERED, DeviceState.FAULT},
}


def can_transition(src: DeviceState, dst: DeviceState) -> bool:
    return dst in _VALID_TRANSITIONS.get(src, set())
