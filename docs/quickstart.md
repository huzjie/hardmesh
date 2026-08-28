# 快速开始

## 1. 环境要求

- Python 3.9+
- （可选）FastAPI + uvicorn 用于完整控制面

## 2. 安装

```bash
git clone https://github.com/huzjie/hardmesh.git
cd hardmesh
pip install -e .            # 内核零依赖，可仅 copy 源码运行
```

## 3. 自检

```bash
python -m hardmesh doctor
```

输出示例：

```
[doctor] 自检开始
  - 设备数: 5
  - 设备: arm, microscope, laser, sensor, thermostat
  - 安全规则: 默认拒绝= True
  - 校准引擎: 迭代上限= 50
[doctor] OK
```

## 4. 你的第一个设备操作

```bash
# 读取温度传感器
python -m hardmesh read sensor-temp-01 --channel temperature

# 移动机械臂
python -m hardmesh act arm-01 move --params '{"joints": "10,20,30,40,50,60"}'

# 执行激光校准
python -m hardmesh calibrate laser-01 --target 0.99
```

## 5. 启动控制面

```bash
python -m hardmesh serve --host 0.0.0.0 --port 8080
```

访问 `http://localhost:8080/healthz` 验证。

## 6. 运行示例

```bash
python examples/demo_calibration.py
```

## 7. 使用 Docker

```bash
docker compose up --build
```

控制面监听 `:8080`，控制台监听 `:5173`。
