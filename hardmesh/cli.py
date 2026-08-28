"""hardmesh 命令行接口。"""
import argparse
import json
import sys
from typing import Optional


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="hardmesh", description="AI 硬件控制网格与实验室自动化平台")
    p.add_argument("--version", action="store_true", help="打印版本")
    sub = p.add_subparsers(dest="command")

    sp_doctor = sub.add_parser("doctor", help="自检（离线可用）")
    sp_doctor.add_argument("--config", default=None, help="JSON 配置路径")

    sp_list = sub.add_parser("list", help="列出设备")
    sp_list.add_argument("--kind", default=None, help="按类型过滤")

    sp_read = sub.add_parser("read", help="读取设备")
    sp_read.add_argument("device_id")
    sp_read.add_argument("--channel", default=None)

    sp_act = sub.add_parser("act", help="触发设备动作")
    sp_act.add_argument("device_id")
    sp_act.add_argument("action")
    sp_act.add_argument("--params", default="{}", help="JSON 参数字符串")

    sp_cal = sub.add_parser("calibrate", help="校准设备")
    sp_cal.add_argument("device_id")
    sp_cal.add_argument("--target", type=float, default=0.99)

    sp_run = sub.add_parser("run", help="执行自然语言硬件任务")
    sp_run.add_argument("task")

    sp_serve = sub.add_parser("serve", help="启动控制面 HTTP 服务")
    sp_serve.add_argument("--host", default="0.0.0.0")
    sp_serve.add_argument("--port", type=int, default=8080)
    sp_serve.add_argument("--no-fastapi", action="store_true", help="强制 stdlib 兜底")

    return p


def _load_context(config_path: Optional[str] = None):
    from hardmesh.config import load_config
    from hardmesh.device.registry import DeviceRegistry
    from hardmesh.device.builtins import all_builtins
    from hardmesh.driver.manager import DriverManager
    from hardmesh.device.state import DeviceState
    from hardmesh.safety.policy import PolicyEngine
    from hardmesh.safety.limits import PhysicalLimits
    from hardmesh.calibration.engine import CalibrationEngine
    from hardmesh.observability.telemetry import Telemetry

    config = load_config(config_path)
    registry = DeviceRegistry()
    manager = DriverManager()
    for desc in all_builtins():
        driver = manager.resolve(desc.driver, desc.connection)
        driver.connect(desc.device_id)
        dev = registry.register_descriptor(desc, driver)
        dev.transition(DeviceState.CONNECTING)
        dev.transition(DeviceState.IDLE)
    policy = PolicyEngine(default_deny=config["safety"]["default_deny"])
    limits = PhysicalLimits(config["safety"]["limits"])
    calib = CalibrationEngine(
        max_iterations=config["calibration"]["max_iterations"],
        tolerance=config["calibration"]["tolerance"],
        optimizer=config["calibration"]["optimizer"],
    )
    telemetry = Telemetry()
    return config, registry, policy, limits, calib, telemetry


def main(argv: Optional[list] = None) -> int:
    args = build_parser().parse_args(argv)

    if args.version:
        from hardmesh import __version__
        print(__version__)
        return 0

    if args.command is None:
        build_parser().print_help()
        return 0

    config, registry, policy, limits, calib, telemetry = _load_context(getattr(args, "config", None))

    if args.command == "doctor":
        print("[doctor] 自检开始")
        print(f"  - 设备数: {len(registry.list())}")
        print("  - 设备:", ", ".join(d.descriptor.kind for d in registry.list()))
        print("  - 安全规则: 默认拒绝=", policy.default_deny)
        print("  - 校准引擎: 迭代上限=", calib.max_iterations)
        print("[doctor] OK")
        return 0

    if args.command == "list":
        for d in registry.filter(kind=args.kind):
            print(f"  {d.device_id:20s} {d.descriptor.kind:12s} {d.name:20s} {d.state.value}")
        return 0

    if args.command == "read":
        dev = registry.get(args.device_id)
        print(json.dumps({"device_id": args.device_id, "value": dev.read(args.channel)},
                         ensure_ascii=False, default=str))
        return 0

    if args.command == "act":
        dev = registry.get(args.device_id)
        params = json.loads(args.params) if args.params else {}
        spec = dev.descriptor.action_by_name(args.action)
        decision = policy.evaluate({"device_id": dev.device_id, "action": args.action,
                                    "risk": spec.risk if spec else "low",
                                    "capability": spec.capability if spec else "actuate",
                                    "params": params})
        if decision["decision"] == "deny":
            print(f"[deny] {decision['reason']}")
            return 1
        limits.check(args.action, params)
        result = dev.act(args.action, **params)
        print(json.dumps(result, ensure_ascii=False, default=str))
        return 0

    if args.command == "calibrate":
        dev = registry.get(args.device_id)
        bounds = {"power": [10.0, 90.0], "wavelength": [600.0, 900.0]}
        result = calib.calibrate(dev, args.target, bounds)
        print(json.dumps(result.to_dict(), ensure_ascii=False, default=str))
        return 0

    if args.command == "run":
        from hardmesh.agent.controller import DeviceController
        ctrl = DeviceController(registry, None)
        out = ctrl.execute(args.task)
        print(json.dumps(out, ensure_ascii=False, default=str))
        return 0

    if args.command == "serve":
        from http.server import HTTPServer
        from hardmesh.api.app import HardmeshContext, create_app
        context = HardmeshContext(registry, policy, calib, telemetry)
        app, stdlib = create_app(context, use_fastapi=not args.no_fastapi)
        if not stdlib:
            import uvicorn
            uvicorn.run(app, host=args.host, port=args.port)
        else:
            server = HTTPServer((args.host, args.port), app)
            print(f"hardmesh 控制面 (stdlib) 监听 http://{args.host}:{args.port}")
            server.serve_forever()
        return 0

    print("未知命令")
    return 1


if __name__ == "__main__":
    sys.exit(main())
