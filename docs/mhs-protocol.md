# MHS 协议

## 消息模型

MHS（Model Hardware Standard）消息为 UTF-8 JSON，核心字段：

| 字段 | 类型 | 说明 |
|---|---|---|
| operation | string | read / write / act / stream / event / ack / error |
| device | string | 目标设备 ID |
| action | string | 动作名（act 时必填） |
| params | object | 动作参数 |
| channel | string | 读写通道 |
| value | any | 写入值 |
| request_id | string | 请求唯一标识 |

## 编解码

```python
from hardmesh.protocol.mhs import Message, encode_message, decode_message

msg = Message(operation="act", device="arm-01", action="move", params={"joints": "0,0,0,0,0,0"})
data = encode_message(msg)       # -> bytes
decoded = decode_message(data)   # -> Message
```

## 路由

`MessageRouter.dispatch` 将消息分发到注册中心中的目标设备，执行 read/write/act，并在设备不存在时抛出 `ProtocolError`。

## 校验

`validate_message` 校验操作类型合法性，`read/write/act` 必须携带 `device`，`act` 必须携带 `action`。
