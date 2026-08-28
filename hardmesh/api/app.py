"""API 应用工厂：优先 FastAPI，无则 stdlib http.server 兜底。"""
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict, Optional
from urllib.parse import urlparse, parse_qs


class HardmeshContext:
    """API 运行上下文，注入 registry / policy / calibration / telemetry 等。"""

    def __init__(self, registry, policy=None, calibration=None,
                 telemetry=None, approval=None):
        self.registry = registry
        self.policy = policy
        self.calibration = calibration
        self.telemetry = telemetry
        self.approval = approval


def create_app(context: HardmeshContext, use_fastapi: bool = True):
    """返回 (app, 是否 stdlib 兜底)。FastAPI 不可用时回退 stdlib。"""
    if use_fastapi:
        try:
            import fastapi  # noqa: WPS433
            return _build_fastapi(context), False
        except ImportError:
            pass
    return _build_stdlib_handler(context), True


def _build_fastapi(context: HardmeshContext):
    import fastapi
    app = fastapi.FastAPI(title="hardmesh", version="0.1.0")

    @app.get("/healthz")
    def healthz():
        return {"status": "ok", "devices": len(context.registry.list())}

    @app.get("/readyz")
    def readyz():
        return {"status": "ready"}

    @app.get("/devices")
    def list_devices():
        return {"devices": context.registry.snapshot()}

    @app.get("/devices/{device_id}")
    def get_device(device_id: str):
        return context.registry.get(device_id).snapshot()

    @app.get("/devices/{device_id}/read")
    def read_device(device_id: str, channel: str = None):
        dev = context.registry.get(device_id)
        return {"device_id": device_id, "value": dev.read(channel)}

    @app.post("/devices/{device_id}/act")
    def act_device(device_id: str, body: dict):
        dev = context.registry.get(device_id)
        action = body.get("action", "")
        params = body.get("params", {})
        _guard(context, dev, action, params)
        result = dev.act(action, **params)
        return {"device_id": device_id, "action": action, "result": result}

    @app.get("/metrics")
    def metrics():
        if context.telemetry:
            return fastapi.Response(context.telemetry.metrics.render(), media_type="text/plain")
        return ""

    return app


def _build_stdlib_handler(context: HardmeshContext):
    ctx = context

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            parsed = urlparse(self.path)
            path = parsed.path
            qs = parse_qs(parsed.query)
            if path == "/healthz":
                self._json(200, {"status": "ok", "devices": len(ctx.registry.list())})
            elif path == "/readyz":
                self._json(200, {"status": "ready"})
            elif path == "/devices":
                self._json(200, {"devices": ctx.registry.snapshot()})
            elif path.startswith("/devices/") and path.endswith("/read"):
                device_id = path[len("/devices/"):-len("/read")]
                try:
                    value = ctx.registry.get(device_id).read(qs.get("channel", [None])[0])
                    self._json(200, {"device_id": device_id, "value": value})
                except Exception as e:
                    self._json(404, {"error": str(e)})
            elif path == "/metrics":
                body = ctx.telemetry.metrics.render() if ctx.telemetry else ""
                self._text(200, body)
            else:
                self._json(404, {"error": "not found"})

        def do_POST(self):  # noqa: N802
            parsed = urlparse(self.path)
            path = parsed.path
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length).decode("utf-8") or "{}") if length else {}
            if path.startswith("/devices/") and path.endswith("/act"):
                device_id = path[len("/devices/"):-len("/act")]
                try:
                    dev = ctx.registry.get(device_id)
                    action = body.get("action", "")
                    params = body.get("params", {})
                    _guard(ctx, dev, action, params)
                    result = dev.act(action, **params)
                    self._json(200, {"device_id": device_id, "action": action, "result": result})
                except Exception as e:
                    self._json(500, {"error": str(e)})
            else:
                self._json(404, {"error": "not found"})

        def _json(self, code, obj):
            data = json.dumps(obj, ensure_ascii=False, default=str).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _text(self, code, body):
            data = body.encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, format, *args):  # noqa: A002
            pass

    return Handler


def _guard(context, dev, action, params):
    """执行前的安全策略 + 限位 + 审批检查。"""
    if context.policy is not None:
        spec = dev.descriptor.action_by_name(action)
        decision = context.policy.evaluate({
            "device_id": dev.device_id, "capability": spec.capability if spec else "actuate",
            "action": action, "risk": spec.risk if spec else "low", "params": params,
        })
        if decision["decision"] == "deny":
            from hardmesh.errors import SafetyViolation
            raise SafetyViolation(decision["reason"])
        if decision["decision"] == "approve" and context.approval is not None:
            req = context.approval.require({"device_id": dev.device_id, "action": action}, ["ops"])
            from hardmesh.errors import ApprovalRequired
            raise ApprovalRequired(f"操作 {action} 需要审批，请求 ID: {req.request_id}")
