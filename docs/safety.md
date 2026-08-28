# 安全护栏

物理世界的操作不可逆，安全是 hardmesh 的一等公民。

## 策略引擎

拒绝式默认：任何操作必须有匹配规则，否则拒绝。规则带风险等级（low/medium/high/critical），动作有 allow/warn/deny/approve 四种决策。

## 物理限位

对温度、电压、电流、力矩、功率等参数做硬性上限检查，超出即抛 `SafetyViolation`。

## 人工审批

高风险动作（急停、安全关机）触发 N-of-M 审批，未获授权前抛出 `ApprovalRequired`。

## 审计日志

所有操作追加写入 JSONL 审计日志，支持按设备查询，用于合规与溯源。
