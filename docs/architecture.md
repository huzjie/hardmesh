# 架构设计

## 分层架构

hardmesh 采用五层架构，横切能力贯穿各层：

1. **控制面层**（api）：FastAPI 优先，stdlib http.server 兜底
2. **智能体 / 实验 / 校准层**：面向任务的三大编排能力
3. **设备抽象层**（device）：MHS manifest 驱动的统一设备模型
4. **驱动层**（driver）：多协议适配，隔离硬件差异
5. **物理设备**：机械臂、激光器、传感器等

## 设计决策

- **内核零依赖**：`device/driver/protocol/calibration/experiment/safety/storage/observability` 全部基于 Python 标准库，避免运行时依赖地狱
- **配置 JSON + 环境变量**：规避 YAML 解析的复杂度，`__` 表层级，支持容器环境注入
- **拒绝式默认**：安全策略默认 deny，任何未显式允许的操作都被拒绝
- **mock 可离线**：Mock 驱动与 Mock Provider 用确定性哈希输出，保证无网络/无硬件也能端到端演示
- **驱动回退**：`DriverManager` 在驱动不可用/未注册时回退 mock，保证系统永远可启动

## 状态机

设备状态机：`unregistered → registered → connecting → idle ⇄ busy/calibrating → fault/estop → offline`

所有状态迁移经 `can_transition` 校验，非法迁移被拒绝。
