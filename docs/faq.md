# FAQ

**Q: 内核真的零依赖吗？**
A: 是。`device/driver/protocol/calibration/experiment/safety/storage/observability` 仅用 Python 标准库。FastAPI、pyserial、pyvisa、paho-mqtt 均为可选依赖。

**Q: 没有硬件能跑吗？**
A: 能。默认 mock 驱动 + mock Provider，端到端离线可演示。

**Q: 如何接入真实设备？**
A: 编写/选择对应协议的 Driver，在 DeviceDescriptor 中指定 `driver` 与 `connection` 参数即可。

**Q: 安全如何保证？**
A: 拒绝式默认策略 + 物理限位 + 人工审批 + 审计日志，接入真实设备前请审慎配置。
