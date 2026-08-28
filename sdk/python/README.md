# hardmesh Python SDK

控制面 HTTP 客户端的 Python 实现，零第三方依赖。

```python
from hardmesh_sdk import HardmeshClient

client = HardmeshClient("http://localhost:8080")
print(client.health())
print(client.list_devices())
print(client.read("sensor-temp-01"))
client.act("arm-01", "home")
```
