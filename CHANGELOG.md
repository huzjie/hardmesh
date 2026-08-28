# 变更日志

## [0.1.0] - 2026-08-28

### 新增
- 设备抽象层（MHS manifest）：descriptor/registry/capability/state + 5 类内置设备
- 多协议驱动：mock/tcp/http/serial/gpib/modbus/mqtt
- MHS 协议层：消息编解码/schema 校验/路由
- 闭环校准引擎：稳定率/精度目标 + 网格/随机/爬山优化器
- 自动化实验编排：工作流/自修复重试/调度器
- 安全护栏：策略引擎/物理限位/审批/审计
- 9 家 LLM Provider + mock
- FastAPI/stdlib 控制面 + CLI + Python/TS SDK + React 控制台
- 可观测性：Prometheus + W3C Tracing + 遥测
- Docker/K8s/Helm/CI/CodeQL
- 完整文档 12 篇 + 端到端示例
