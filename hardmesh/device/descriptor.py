"""设备描述符（MHS manifest）：声明设备的身份、能力、动作与参数。"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ParameterSpec:
    """动作参数规格。"""
    name: str
    type: str = "float"                 # float/int/bool/str/enum
    required: bool = False
    default: Any = None
    unit: str = ""
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    description: str = ""
    enum: List[str] = field(default_factory=list)

    def validate(self, value: Any) -> Any:
        if value is None:
            if self.required:
                raise ValueError(f"参数 {self.name} 必填")
            return self.default
        if self.type == "float":
            value = float(value)
        elif self.type == "int":
            value = int(value)
        elif self.type == "bool":
            value = bool(value)
        elif self.type == "str":
            value = str(value)
        elif self.type == "enum":
            value = str(value)
            if self.enum and value not in self.enum:
                raise ValueError(f"参数 {self.name} 取值须在 {self.enum} 中")
        if self.minimum is not None and value < self.minimum:
            raise ValueError(f"参数 {self.name} 小于下限 {self.minimum}")
        if self.maximum is not None and value > self.maximum:
            raise ValueError(f"参数 {self.name} 大于上限 {self.maximum}")
        return value


@dataclass
class ActionSpec:
    """动作规格。"""
    name: str
    description: str = ""
    parameters: List[ParameterSpec] = field(default_factory=list)
    capability: str = "actuate"
    risk: str = "low"                    # low/medium/high/critical
    reversible: bool = True


@dataclass
class DeviceDescriptor:
    """设备描述符，等价于 MHS 的设备 manifest。"""
    device_id: str
    name: str
    kind: str                            # arm/microscope/laser/sensor/...
    manufacturer: str = ""
    model: str = ""
    version: str = "0.0.0"
    capabilities: List[str] = field(default_factory=list)
    actions: List[ActionSpec] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)
    driver: str = "mock"
    connection: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "device_id": self.device_id,
            "name": self.name,
            "kind": self.kind,
            "manufacturer": self.manufacturer,
            "model": self.model,
            "version": self.version,
            "capabilities": self.capabilities,
            "actions": [
                {
                    "name": a.name,
                    "description": a.description,
                    "parameters": [
                        {
                            "name": p.name, "type": p.type, "required": p.required,
                            "default": p.default, "unit": p.unit,
                            "minimum": p.minimum, "maximum": p.maximum,
                            "description": p.description, "enum": p.enum,
                        } for p in a.parameters
                    ],
                    "capability": a.capability,
                    "risk": a.risk,
                    "reversible": a.reversible,
                } for a in self.actions
            ],
            "properties": self.properties,
            "driver": self.driver,
            "connection": self.connection,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "DeviceDescriptor":
        actions = [
            ActionSpec(
                name=a["name"],
                description=a.get("description", ""),
                parameters=[
                    ParameterSpec(
                        name=p["name"], type=p.get("type", "float"),
                        required=p.get("required", False),
                        default=p.get("default"), unit=p.get("unit", ""),
                        minimum=p.get("minimum"), maximum=p.get("maximum"),
                        description=p.get("description", ""),
                        enum=p.get("enum", []),
                    ) for p in a.get("parameters", [])
                ],
                capability=a.get("capability", "actuate"),
                risk=a.get("risk", "low"),
                reversible=a.get("reversible", True),
            ) for a in d.get("actions", [])
        ]
        return cls(
            device_id=d["device_id"], name=d.get("name", d["device_id"]),
            kind=d.get("kind", "generic"), manufacturer=d.get("manufacturer", ""),
            model=d.get("model", ""), version=d.get("version", "0.0.0"),
            capabilities=d.get("capabilities", []), actions=actions,
            properties=d.get("properties", {}), driver=d.get("driver", "mock"),
            connection=d.get("connection", {}), tags=d.get("tags", []),
        )

    def action_by_name(self, name: str) -> Optional[ActionSpec]:
        for a in self.actions:
            if a.name == name:
                return a
        return None
