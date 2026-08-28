# SDK 使用

## Python SDK

```python
from hardmesh_sdk import HardmeshClient
client = HardmeshClient("http://localhost:8080")
print(client.health())
print(client.list_devices())
print(client.read("sensor-temp-01", "temperature"))
client.act("arm-01", "home")
```

## TypeScript SDK

```typescript
import { HardmeshClient } from "hardmesh-sdk";
const client = new HardmeshClient("http://localhost:8080");
const devices = await client.listDevices();
await client.act("arm-01", "home");
```
