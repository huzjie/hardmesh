"""消息路由：把 MHS 消息分发到注册中心中的目标设备。"""
from typing import Any, Dict, Optional

from hardmesh.device.registry import DeviceRegistry
from hardmesh.errors import DeviceNotFound, ProtocolError
from hardmesh.protocol.mhs import Message, MessageType
from hardmesh.protocol.schema import validate_message


class MessageRouter:
    """将协议消息路由到设备操作。"""

    def __init__(self, registry: DeviceRegistry):
        self.registry = registry

    def dispatch(self, msg: Message) -> Dict[str, Any]:
        validate_message(msg)
        op = msg.operation
        if op in (MessageType.READ.value, MessageType.WRITE.value, MessageType.ACT.value):
            try:
                device = self.registry.get(msg.device)
            except DeviceNotFound as e:
                raise ProtocolError(str(e))
            if op == MessageType.READ.value:
                return {"operation": op, "device": msg.device,
                        "result": device.read(msg.channel or None)}
            if op == MessageType.WRITE.value:
                return {"operation": op, "device": msg.device,
                        "result": device.write(msg.channel, msg.value)}
            if op == MessageType.ACT.value:
                return {"operation": op, "device": msg.device,
                        "result": device.act(msg.action, **msg.params)}
        if op == MessageType.ACK.value:
            return {"operation": op, "request_id": msg.request_id, "ack": True}
        if op == MessageType.EVENT.value:
            return {"operation": op, "device": msg.device, "payload": msg.payload}
        if op == MessageType.STREAM.value:
            return {"operation": op, "device": msg.device, "subscribed": True}
        raise ProtocolError(f"未处理的操作 {op}")
