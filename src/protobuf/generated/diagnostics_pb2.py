# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: diagnostics.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='diagnostics.proto',
  package='',
  syntax='proto3',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x11\x64iagnostics.proto\"{\n\x0e\x64iagnostics_v1\x12\x35\n\x0b\x64iagnostics\x18\x01 \x03(\x0b\x32 .diagnostics_v1.DiagnosticsEntry\x1a\x32\n\x10\x44iagnosticsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\x62\x06proto3'
)




_DIAGNOSTICS_V1_DIAGNOSTICSENTRY = _descriptor.Descriptor(
  name='DiagnosticsEntry',
  full_name='diagnostics_v1.DiagnosticsEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='diagnostics_v1.DiagnosticsEntry.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='value', full_name='diagnostics_v1.DiagnosticsEntry.value', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=b'8\001',
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=94,
  serialized_end=144,
)

_DIAGNOSTICS_V1 = _descriptor.Descriptor(
  name='diagnostics_v1',
  full_name='diagnostics_v1',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='diagnostics', full_name='diagnostics_v1.diagnostics', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[_DIAGNOSTICS_V1_DIAGNOSTICSENTRY, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=21,
  serialized_end=144,
)

_DIAGNOSTICS_V1_DIAGNOSTICSENTRY.containing_type = _DIAGNOSTICS_V1
_DIAGNOSTICS_V1.fields_by_name['diagnostics'].message_type = _DIAGNOSTICS_V1_DIAGNOSTICSENTRY
DESCRIPTOR.message_types_by_name['diagnostics_v1'] = _DIAGNOSTICS_V1
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

diagnostics_v1 = _reflection.GeneratedProtocolMessageType('diagnostics_v1', (_message.Message,), {

  'DiagnosticsEntry' : _reflection.GeneratedProtocolMessageType('DiagnosticsEntry', (_message.Message,), {
    'DESCRIPTOR' : _DIAGNOSTICS_V1_DIAGNOSTICSENTRY,
    '__module__' : 'diagnostics_pb2'
    # @@protoc_insertion_point(class_scope:diagnostics_v1.DiagnosticsEntry)
    })
  ,
  'DESCRIPTOR' : _DIAGNOSTICS_V1,
  '__module__' : 'diagnostics_pb2'
  # @@protoc_insertion_point(class_scope:diagnostics_v1)
  })
_sym_db.RegisterMessage(diagnostics_v1)
_sym_db.RegisterMessage(diagnostics_v1.DiagnosticsEntry)


_DIAGNOSTICS_V1_DIAGNOSTICSENTRY._options = None
# @@protoc_insertion_point(module_scope)
