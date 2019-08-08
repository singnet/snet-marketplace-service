# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: merckledag.proto

from google.protobuf import symbol_database as _symbol_database
from google.protobuf import reflection as _reflection
from google.protobuf import message as _message
from google.protobuf import descriptor as _descriptor
import sys
_b = sys.version_info[0] < 3 and (
    lambda x: x) or (lambda x: x.encode('latin1'))
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor.FileDescriptor(
    name='merckledag.proto',
    package='',
    syntax='proto2',
    serialized_options=None,
    serialized_pb=_b('\n\x10merckledag.proto\"7\n\nMerkleLink\x12\x0c\n\x04Hash\x18\x01 \x02(\x0c\x12\x0c\n\x04Name\x18\x02 \x02(\t\x12\r\n\x05Tsize\x18\x03 \x02(\x04\"6\n\nMerkleNode\x12\x1a\n\x05Links\x18\x02 \x03(\x0b\x32\x0b.MerkleLink\x12\x0c\n\x04\x44\x61ta\x18\x01 \x02(\x0c')
)


_MERKLELINK = _descriptor.Descriptor(
    name='MerkleLink',
    full_name='MerkleLink',
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    fields=[
        _descriptor.FieldDescriptor(
            name='Hash', full_name='MerkleLink.Hash', index=0,
            number=1, type=12, cpp_type=9, label=2,
            has_default_value=False, default_value=_b(""),
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='Name', full_name='MerkleLink.Name', index=1,
            number=2, type=9, cpp_type=9, label=2,
            has_default_value=False, default_value=_b("").decode('utf-8'),
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='Tsize', full_name='MerkleLink.Tsize', index=2,
            number=3, type=4, cpp_type=4, label=2,
            has_default_value=False, default_value=0,
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR),
    ],
    extensions=[
    ],
    nested_types=[],
    enum_types=[
    ],
    serialized_options=None,
    is_extendable=False,
    syntax='proto2',
    extension_ranges=[],
    oneofs=[
    ],
    serialized_start=20,
    serialized_end=75,
)


_MERKLENODE = _descriptor.Descriptor(
    name='MerkleNode',
    full_name='MerkleNode',
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    fields=[
        _descriptor.FieldDescriptor(
            name='Links', full_name='MerkleNode.Links', index=0,
            number=2, type=11, cpp_type=10, label=3,
            has_default_value=False, default_value=[],
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='Data', full_name='MerkleNode.Data', index=1,
            number=1, type=12, cpp_type=9, label=2,
            has_default_value=False, default_value=_b(""),
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR),
    ],
    extensions=[
    ],
    nested_types=[],
    enum_types=[
    ],
    serialized_options=None,
    is_extendable=False,
    syntax='proto2',
    extension_ranges=[],
    oneofs=[
    ],
    serialized_start=77,
    serialized_end=131,
)

_MERKLENODE.fields_by_name['Links'].message_type = _MERKLELINK
DESCRIPTOR.message_types_by_name['MerkleLink'] = _MERKLELINK
DESCRIPTOR.message_types_by_name['MerkleNode'] = _MERKLENODE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

MerkleLink = _reflection.GeneratedProtocolMessageType('MerkleLink', (_message.Message,), dict(
    DESCRIPTOR=_MERKLELINK,
    __module__='merckledag_pb2'
    # @@protoc_insertion_point(class_scope:MerkleLink)
))
_sym_db.RegisterMessage(MerkleLink)

MerkleNode = _reflection.GeneratedProtocolMessageType('MerkleNode', (_message.Message,), dict(
    DESCRIPTOR=_MERKLENODE,
    __module__='merckledag_pb2'
    # @@protoc_insertion_point(class_scope:MerkleNode)
))
_sym_db.RegisterMessage(MerkleNode)


# @@protoc_insertion_point(module_scope)
