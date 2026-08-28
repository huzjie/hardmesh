"""MHS 协议测试。"""
from hardmesh.errors import ProtocolError
from hardmesh.protocol.mhs import Message, MessageType, decode_message, encode_message
from hardmesh.protocol.schema import validate_message


def test_roundtrip():
    msg = Message(operation="act", device="arm-01", action="move",
                  params={"joints": "0,0,0,0,0,0"})
    decoded = decode_message(encode_message(msg))
    assert decoded.operation == "act"
    assert decoded.device == "arm-01"
    assert decoded.action == "move"


def test_validate_missing_device():
    msg = Message(operation="read", device="")
    try:
        validate_message(msg)
        assert False
    except ProtocolError:
        assert True


def test_validate_bad_operation():
    msg = Message(operation="hack", device="x")
    try:
        validate_message(msg)
        assert False
    except ProtocolError:
        assert True


def test_message_types():
    assert "read" in [m.value for m in MessageType]
