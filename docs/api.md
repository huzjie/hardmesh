# API 参考

## 端点

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | /healthz | 健康检查 |
| GET | /readyz | 就绪检查 |
| GET | /devices | 列出所有设备 |
| GET | /devices/{id} | 设备详情 |
| GET | /devices/{id}/read?channel= | 读取设备 |
| POST | /devices/{id}/act | 触发动作（body: {action, params}） |
| GET | /metrics | Prometheus 指标 |

## 示例

```bash
curl http://localhost:8080/devices
curl "http://localhost:8080/devices/sensor-temp-01/read?channel=temperature"
curl -X POST http://localhost:8080/devices/arm-01/act \
  -H "Content-Type: application/json" \
  -d '{"action": "home", "params": {}}'
```
