"""MHS（Model Hardware Standard）消息编解码。

消息为 UTF-8 JSON，字段对齐 Anthropic MHS 研究预览的核心语义：
``operation`` / ``device`` / ``action`` / ``params`` / ``request_id``。
"""
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict
from uuid import uuid4

from hardmesh.errors import ProtocolError


class MessageType(str, Enum):
    READ = "read"
    WRITE = "write"
    ACT = "act"
    STREAM = "stream"
    EVENT = "event"
    ACK = "ack"
    ERROR = "error"


@dataclass
class Message:
    operation: str
    device: str = ""
    action: str = ""
    params: Dict[str, Any] = field(default_factory=dict)
    channel: str = ""
    value: Any = None
    request_id: str = field(default_factory=lambda: uuid4().hex)
    payload: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "operation": self.operation,
            "device": self.device,
            "request_id": self.request_id,
        }
        if self.action:
            d["action"] = self.action
        if self.channel:
            d["channel"] = self.channel
        if self.value is not None:
            d["value"] = self.value
        if self.params:
            d["params"] = self.params
        if self.payload:
            d["payload"] = self.payload
        return d


def encode_message(msg: Message) -> bytes:
    return json.dumps(msg.to_dict(), ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def decode_message(data: bytes) -> Message:
    try:
        d = json.loads(data.decode("utf-8"))
    except (ValueError, UnicodeDecodeError) as e:
        raise ProtocolError(f"消息解码失败: {e}")
    if not isinstance(d, dict) or "operation" not in d:
        raise ProtocolError("消息缺少 operation 字段")
    return Message(
        operation=d["operation"],
        device=d.get("device", ""),
        action=d.get("action", ""),
        params=d.get("params", {}),
        channel=d.get("channel", ""),
        value=d.get("value"),
        request_id=d.get("request_id", uuid4().hex),
        payload=d.get("payload", {}),
    )
