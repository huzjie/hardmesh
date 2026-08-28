# 校准引擎

## 背景

Anthropic MHS 案例中，Claude 将 QuEra 量子计算机激光校准的稳定率从 58% 提升至 99.3%。hardmesh 把「闭环校准」抽象为可复用引擎。

## 核心组件

- **ObjectiveFunction**：把参数映射到 [0,1] 得分（稳定率 / 精度）
- **Optimizer**：网格 / 随机 / 爬山优化器
- **CalibrationLoop**：设参数 → 测量 → 评估 → 收敛判断
- **CalibrationEngine**：包装设备 `calibrate` 能力的高层接口

## 指标

- **稳定率** = `max(0, 1 - CV)`，CV 为变异系数
- **精度** = `1 - |均值-目标|/|目标|`

## 使用

```python
from hardmesh.calibration.engine import CalibrationEngine
engine = CalibrationEngine(max_iterations=50, tolerance=0.001)
result = engine.calibrate(laser_dev, target=0.99,
                          param_bounds={"power": [10.0, 90.0]})
print(result.score, result.converged, result.iterations)
```
