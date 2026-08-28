# 设备驱动

## 内置驱动

| 驱动 | 协议 | 依赖 |
|---|---|---|
| mock | 本地模拟 | 无 |
| tcp | TCP socket | 无 |
| http | HTTP/REST | 无 |
| serial | RS-232/485 | pyserial（可选） |
| gpib | VISA/GPIB | pyvisa（可选） |
| modbus | Modbus TCP | 无 |
| mqtt | MQTT | paho-mqtt（可选） |

## 开发自定义驱动

```python
from hardmesh.driver.base import Driver

class MyDriver(Driver):
    name = "my"

    def connect(self, device_id): ...
    def read(self, device_id, channel=None): ...
    def write(self, device_id, channel, value): ...
    def act(self, device_id, action, params): ...
```

## 注册

```python
manager = DriverManager()
manager.register_class("my", MyDriver)
driver = manager.resolve("my", {"host": "..."})
```
