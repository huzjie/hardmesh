"""消息 schema 校验：确保入站消息操作类型合法。"""
from typing import Dict, List

from hardmesh.errors import ProtocolError
from hardmesh.protocol.mhs import Message, MessageType

_VALID_OPERATIONS: List[str] = [m.value for m in MessageType]


def validate_message(msg: Message) -> Message:
    if msg.operation not in _VALID_OPERATIONS:
        raise ProtocolError(
            f"非法操作 {msg.operation}，合法值为 {_VALID_OPERATIONS}"
        )
    if msg.operation in (MessageType.READ.value, MessageType.WRITE.value,
                         MessageType.ACT.value) and not msg.device:
        raise ProtocolError("read/write/act 操作必须携带 device 字段")
    if msg.operation == MessageType.ACT.value and not msg.action:
        raise ProtocolError("act 操作必须携带 action 字段")
    return msg


def valid_operations() -> List[str]:
    return list(_VALID_OPERATIONS)


def describe() -> Dict[str, str]:
    return {
        "read": "读取设备测量值/状态",
        "write": "写入设备设定值",
        "act": "触发设备物理动作",
        "stream": "订阅设备数据流",
        "event": "设备主动上报事件",
        "ack": "操作确认",
        "error": "错误回报",
    }
