"""Modbus RTU/TCP 工业协议驱动：面向 PLC / 工业传感器。"""
import struct
import socket
from typing import Any, Optional

from hardmesh.driver.base import Driver
from hardmesh.errors import DriverError


def _crc16(data: bytes) -> int:
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc


class ModbusDriver(Driver):
    name = "modbus"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self.host = self.config.get("host", "127.0.0.1")
        self.port = int(self.config.get("port", 502))
        self.unit = int(self.config.get("unit", 1))
        self.timeout = float(self.config.get("timeout", 3.0))

    def _read_holding(self, address: int, count: int = 1) -> list:
        req = struct.pack(">BBHHH", 0x01, 0x03, address, count, 0)
        # Modbus TCP: transaction(2) + protocol(2) + length(2) + unit(1) + pdu
        header = struct.pack(">HHHB", 1, 0, len(req) + 1, self.unit)
        frame = header + req
        try:
            with socket.create_connection((self.host, self.port), timeout=self.timeout) as s:
                s.sendall(frame)
                resp = s.recv(9 + count * 2)
        except OSError as e:
            raise DriverError(f"Modbus 通信失败: {e}")
        if len(resp) < 9:
            raise DriverError("Modbus 响应过短")
        byte_count = resp[8]
        regs = struct.unpack(">" + "H" * (byte_count // 2), resp[9:9 + byte_count])
        return list(regs)

    def read(self, device_id: str, channel: Optional[str] = None) -> Any:
        addr = int(channel or 0)
        vals = self._read_holding(addr, 1)
        return vals[0] if vals else 0

    def write(self, device_id: str, channel: str, value: Any) -> Any:
        address = int(channel)
        val = int(value)
        req = struct.pack(">BBHHH", 0x01, 0x06, address, val, 0)
        header = struct.pack(">HHHB", 1, 0, len(req) + 1, self.unit)
        try:
            with socket.create_connection((self.host, self.port), timeout=self.timeout) as s:
                s.sendall(header + req)
                s.recv(12)
        except OSError as e:
            raise DriverError(f"Modbus 写入失败: {e}")
        return {"ack": True, "address": address, "value": val}

    def act(self, device_id: str, action: str, params: dict) -> Any:
        return self.write(device_id, params.get("channel", "0"), params.get("value", 0))
