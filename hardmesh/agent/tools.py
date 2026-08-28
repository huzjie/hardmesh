"""把设备操作封装为 LLM 可调用的工具描述。"""
from typing import Any, Dict, List

from hardmesh.device.registry import DeviceRegistry


def build_tool_definitions(registry: DeviceRegistry) -> List[Dict[str, Any]]:
    """把注册中心里的设备能力导出为 function-calling 工具定义。"""
    tools: List[Dict[str, Any]] = []
    tools.append({
        "name": "list_devices",
        "description": "列出所有已注册的硬件设备及其能力",
        "parameters": {"type": "object", "properties": {}},
    })
    for dev in registry.list():
        tools.append({
            "name": f"read_{dev.device_id.replace('-', '_')}",
            "description": f"读取设备 {dev.name}({dev.device_id}) 的测量值",
            "parameters": {
                "type": "object",
                "properties": {"channel": {"type": "string", "description": "通道名（可选）"}},
            },
        })
        for a in dev.descriptor.actions:
            props = {}
            for p in a.parameters:
                props[p.name] = {"type": p.type if p.type in ("float", "int", "bool", "str") else "string",
                                 "description": p.description or p.name}
            tools.append({
                "name": f"{a.name}_{dev.device_id.replace('-', '_')}",
                "description": f"{a.description or a.name}（设备 {dev.name}，风险 {a.risk}）",
                "parameters": {"type": "object", "properties": props,
                               "required": [p.name for p in a.parameters if p.required]},
            })
    return tools


def execute_tool(registry: DeviceRegistry, name: str, args: Dict[str, Any]) -> Any:
    """执行一个具名工具调用。"""
    if name == "list_devices":
        return registry.snapshot()
    if name.startswith("read_"):
        device_id = name[5:].replace("_", "-")
        return registry.get(device_id).read(args.get("channel"))
    parts = name.rsplit("_", 1)
    if len(parts) == 2:
        action, device_id = parts[0], parts[1].replace("_", "-")
        try:
            dev = registry.get(device_id)
        except Exception:
            return {"error": f"设备 {device_id} 不存在"}
        return dev.act(action, **args)
    return {"error": f"未知工具 {name}"}
