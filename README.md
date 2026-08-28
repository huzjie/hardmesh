# hardmesh

**AI 硬件控制网格与实验室自动化平台** —— Anthropic MHS（Model Hardware Standard，模型硬件标准）的企业级落地实现。

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![CI](https://img.shields.io/badge/CI-GitHub%20Actions-2088FF.svg)](.github/workflows/ci.yml)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](Dockerfile)

> **热点背景**：2026-08-28，Anthropic 发布 **MHS（模型硬件标准）** 第一阶段研究预览——被称为「硬件版 MCP」，让 Claude 直接读取并操控机械臂、显微镜、量子计算机激光系统等**真实物理设备**。在 QuEra 量子计算机的激光校准中，Claude 将稳定率从人类专家的 **58% 提升至 99.3%**，单次校准从 5–10 分钟压缩到 **6 秒**；Genentech 的药物发现实验也由 Claude 自主运行并自修复。AI 的能力边界正从「软件世界」走向「物理世界」。

**hardmesh** 把这一范式落地为可部署、可扩展、可审计的完整平台：**设备抽象 + 多协议驱动 + 闭环校准 + 安全护栏 + 自动化实验 + LLM 智能体控制**。内核**纯 Python 标准库零第三方运行时依赖**，`mock` 模式完全离线可跑。

---

## ✨ 核心特性

- 🔌 **设备抽象层（MHS Manifest）**：统一描述设备身份、能力、动作与参数规格，声明式注册机械臂 / 显微镜 / 激光器 / 传感器 / 恒温器等
- 🔗 **多协议驱动**：串口（RS-232/485）、TCP、HTTP/REST、GPIB/VISA、Modbus、MQTT、以及离线确定性 Mock 驱动，即插即用
- 📡 **MHS 协议层**：JSON 消息编解码 + schema 校验 + 消息路由，对齐 MHS 的 `operation/device/action/params` 语义
- 🎯 **闭环校准引擎**：稳定率 / 精度目标函数 + 网格/随机/爬山优化器 + 收敛判断，复刻「58%→99.3%」的校准范式
- 🧪 **自动化实验编排**：声明式工作流（依赖拓扑 + 串并行执行）+ 自修复重试 + 任务调度
- 🛡️ **安全护栏**：拒绝式默认策略引擎 + 物理限位（温度/电压/电流/力矩）+ N-of-M 人工审批 + 追加式审计日志
- 🤖 **LLM 智能体控制**：9 家 Provider（OpenAI/Anthropic/DeepSeek/Qwen/Kimi/GLM/Gemini/Ollama/mock）+ ReAct 循环 + 工具封装
- 📊 **可观测性**：Prometheus 指标 + W3C Trace Context + 遥测聚合
- 🖥️ **双形态控制面**：FastAPI 优先 + stdlib 兜底 HTTP 服务器 + CLI
- 📦 **完整工程化**：Python/TypeScript 双 SDK + React 深色控制台 + Docker/K8s/Helm/CI/CodeQL

---

## 🚀 快速开始

```bash
git clone https://github.com/huzjie/hardmesh.git
cd hardmesh

# 自检（离线可用，会加载 5 类内置 mock 设备）
python -m hardmesh doctor

# 列出设备
python -m hardmesh list

# 读取温度传感器
python -m hardmesh read sensor-temp-01 --channel temperature

# 触发机械臂动作（回机械原点）
python -m hardmesh act arm-01 home

# 执行激光闭环校准
python -m hardmesh calibrate laser-01 --target 0.99

# 自然语言硬件任务（mock 模式规则规划）
python -m hardmesh run "校准激光器并读取温度"

# 启动控制面（FastAPI + HTTP）
python -m hardmesh serve --host 0.0.0.0 --port 8080
```

端到端示例：

```bash
python examples/demo_calibration.py      # 策略评估 + 闭环校准 + 读数
python examples/register_device.py       # 注册自定义设备并执行动作
python examples/experiment_workflow.py   # 声明式实验工作流 + 自修复
```

---

## 🧩 架构总览

```
                         ┌──────────────────────────────┐
                         │        控制面 (FastAPI/HTTP)    │
                         │   /devices /read /act /metrics │
                         └───────────────┬──────────────┘
                                         │
   ┌──────────────┐   ┌──────────────┐   │   ┌──────────────┐
   │  智能体层      │   │  实验编排层    │   │   │  校准引擎层    │
   │ planner/loop │   │ workflow/    │   │   │ objective/   │
   │ tools/ctrl   │   │ retry/sched  │   │   │ optimizer    │
   └──────┬───────┘   └──────┬───────┘   │   └──────┬───────┘
          │                  │           │          │
          └──────────────────┼───────────┼──────────┘
                             ▼           ▼
                     ┌────────────────────────┐
                     │      设备抽象层 (MHS)      │
                     │  descriptor/registry/    │
                     │  capability/state        │
                     └────────────┬───────────┘
                                  │
                     ┌────────────▼───────────┐
                     │       驱动层 (多协议)      │
                     │ mock/tcp/http/serial/   │
                     │ gpib/modbus/mqtt        │
                     └────────────┬───────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              ▼                   ▼                   ▼
        ┌──────────┐       ┌──────────┐        ┌──────────┐
        │ 机械臂     │       │ 激光器    │        │ 传感器    │
        └──────────┘       └──────────┘        └──────────┘

   横切能力：安全护栏(safety) · 可观测(observability) · 存储(storage)
```

---

## 📁 项目结构

```
hardmesh/
├── hardmesh/                 # Python 内核（纯标准库零依赖）
│   ├── device/               # 设备抽象层：descriptor/registry/capability/state/builtins
│   ├── driver/               # 多协议驱动：mock/tcp/http/serial/gpib/modbus/mqtt
│   ├── protocol/             # MHS 协议：mhs/schema/router
│   ├── calibration/          # 校准引擎：objective/optimizer/loop/metrics/engine
│   ├── experiment/           # 实验编排：workflow/retry/scheduler/observation
│   ├── agent/                # 智能体：planner/loop/tools/controller
│   ├── providers/            # 9 家 LLM Provider + mock
│   ├── safety/               # 安全护栏：policy/rules/approval/limits/audit
│   ├── storage/              # SQLite 存储
│   ├── observability/        # Prometheus + W3C Tracing + 遥测
│   ├── api/                  # FastAPI + stdlib 兜底控制面
│   └── cli.py / __main__.py  # 命令行入口
├── sdk/
│   ├── python/               # Python SDK（stdlib urllib）
│   └── typescript/           # TypeScript SDK
├── web/                      # React 深色控制台
├── examples/                 # 端到端示例
├── k8s/                      # Kubernetes 部署清单
├── helm/hardmesh/            # Helm Chart
├── docs/                     # 完整文档
├── .github/workflows/        # CI / CodeQL / Release
├── Dockerfile / docker-compose.yml
└── pyproject.toml / requirements.txt
```

---

## ⚙️ 配置

配置采用 **JSON 文件 + `HARDMESH_*` 环境变量**（`__` 表示层级），内核零依赖：

```bash
# 环境变量覆盖（等价于 JSON 中的 safety.limits.max_voltage_v）
export HARDMESH_SAFETY__LIMITS__MAX_VOLTAGE_V=24.0
export HARDMESH_CALIBRATION__MAX_ITERATIONS=100
```

完整配置见 [`config.example.json`](config.example.json)。

---

## 📚 文档

| 文档 | 说明 |
|---|---|
| [快速开始](docs/quickstart.md) | 安装、配置、首个示例 |
| [架构设计](docs/architecture.md) | 分层架构与设计决策 |
| [MHS 协议](docs/mhs-protocol.md) | 消息编解码与路由 |
| [设备驱动](docs/device-driver.md) | 多协议驱动开发指南 |
| [校准引擎](docs/calibration.md) | 闭环校准原理与实践 |
| [安全护栏](docs/safety.md) | 策略 / 限位 / 审批 / 审计 |
| [API 参考](docs/api.md) | 控制面 HTTP 接口 |
| [SDK 使用](docs/sdk.md) | Python / TypeScript SDK |
| [部署指南](docs/deployment.md) | Docker / K8s / Helm |
| [示例集](docs/examples.md) | 端到端示例详解 |
| [FAQ](docs/faq.md) | 常见问题 |
| [路线图](docs/roadmap.md) | 后续规划 |

---

## 🧪 测试

```bash
pip install pytest
pytest -q
```

覆盖设备抽象、状态机、协议编解码、策略引擎、校准指标、优化器、实验工作流、存储与遥测等模块。

---

## 🤝 贡献

见 [CONTRIBUTING.md](CONTRIBUTING.md) 与 [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)。

## 📄 许可

[Apache License 2.0](LICENSE)

> ⚠️ 本项目为 MHS（模型硬件标准）范式的开源参考实现，**不连接任何真实物理设备**（默认 mock 驱动）。接入真实设备前请务必审慎评估安全策略与物理限位配置。
