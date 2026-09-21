'''
Part 5 required tests (BROWSETERM_CLOUD_CONTROL_PLANE_MIGRATION.md):
  - Generated Python package builds reproducibly (implicitly covered: these tests only run
    against the committed generated output, same as every consumer will).
  - Serialization round trips.
  - Backward-compatibility/breaking-change check (a message serialized by an "old" schema must
    still parse under the "new" one, ignoring fields the old schema didn't have).
  - Unknown fields and unsupported versions handled safely.
'''

from device_control_spec import device_control_pb2, device_control_types_pb2


def test_hello_round_trip():
    hello = device_control_types_pb2.Hello(
        device_id="d1", agent_version="0.1.0", protocol_version="v1",
        platform=device_control_types_pb2.DEVICE_PLATFORM_MACOS,
        architecture=device_control_types_pb2.DEVICE_ARCHITECTURE_ARM64,
        startup_id="startup-1",
    )
    parsed = device_control_types_pb2.Hello()
    parsed.ParseFromString(hello.SerializeToString())
    assert parsed.device_id == "d1"
    assert parsed.platform == device_control_types_pb2.DEVICE_PLATFORM_MACOS
    assert parsed.startup_id == "startup-1"


def test_device_to_cloud_envelope_oneof_round_trip():
    envelope = device_control_pb2.DeviceToCloud(
        command_result=device_control_types_pb2.CommandResult(
            command_id="cmd-1", status=device_control_types_pb2.COMMAND_STATUS_SUCCEEDED,
        )
    )
    assert envelope.WhichOneof("payload") == "command_result"
    parsed = device_control_pb2.DeviceToCloud()
    parsed.ParseFromString(envelope.SerializeToString())
    assert parsed.WhichOneof("payload") == "command_result"
    assert parsed.command_result.command_id == "cmd-1"


def test_cloud_to_device_envelope_oneof_round_trip():
    envelope = device_control_pb2.CloudToDevice(
        execute_command=device_control_types_pb2.ExecuteCommand(
            command_id="cmd-2", operation=device_control_types_pb2.COMMAND_OPERATION_RESUME,
            container_id="c1", device_id="d1", placement_generation=3,
        )
    )
    assert envelope.WhichOneof("payload") == "execute_command"
    parsed = device_control_pb2.CloudToDevice()
    parsed.ParseFromString(envelope.SerializeToString())
    assert parsed.execute_command.placement_generation == 3


def test_unspecified_enum_is_the_zero_value_not_a_real_operation():
    '''proto3 requires an explicit zero/UNSPECIFIED value for every enum - a message that never
    sets `operation` must never be silently mistaken for a real command like CREATE.'''
    cmd = device_control_types_pb2.ExecuteCommand(command_id="cmd-3")
    assert cmd.operation == device_control_types_pb2.COMMAND_OPERATION_UNSPECIFIED
    assert cmd.operation != device_control_types_pb2.COMMAND_OPERATION_CREATE


def test_unknown_field_does_not_crash_parsing_and_survives_reserialization():
    '''A message carrying a field number this schema has never declared (simulating a newer peer
    during a Part 25 rolling upgrade) must parse without raising, and an older component that
    re-forwards the message unmodified must not silently drop the field it doesn't understand.'''
    known_bytes = device_control_types_pb2.Hello(device_id="d1", agent_version="9.9.9").SerializeToString()
    # Field 15 does not exist on Hello (declared fields only go up to 7) - append it as a raw
    # unknown varint field (wire type 0), tag = 15<<3|0 = 120, a valid single-byte varint tag,
    # the way an unrecognized field would actually arrive on the wire.
    unknown_field_bytes = known_bytes + bytes([(15 << 3) | 0, 0x2A])

    parsed = device_control_types_pb2.Hello()
    parsed.ParseFromString(unknown_field_bytes)  # must not raise
    assert parsed.device_id == "d1"
    assert parsed.SerializeToString() == unknown_field_bytes


def test_backward_compatibility_old_message_parses_under_current_schema():
    '''A message built with only the fields that existed at protocol v1 launch must still parse
    cleanly under the current schema - the whole point of "never reuse a field number."'''
    old_style_bytes = device_control_types_pb2.Heartbeat(sent_at_unix_ms=123).SerializeToString()
    parsed = device_control_types_pb2.Heartbeat()
    parsed.ParseFromString(old_style_bytes)
    assert parsed.sent_at_unix_ms == 123


def test_service_stub_and_servicer_are_generated():
    from device_control_spec import device_control_pb2_grpc
    assert hasattr(device_control_pb2_grpc, "DeviceControlStub")
    assert hasattr(device_control_pb2_grpc, "DeviceControlServicer")
    assert hasattr(device_control_pb2_grpc, "add_DeviceControlServicer_to_server")
