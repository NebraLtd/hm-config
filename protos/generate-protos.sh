#!/bin/bash
PROTO_DEFINITIONS_PATH="protos/"
PROTO_OUTPUT_PATH="gatewayconfig/protos/"

protoc -I="$PROTO_DEFINITIONS_PATH" --python_out="$PROTO_OUTPUT_PATH" add_gateway.proto
protoc -I="$PROTO_DEFINITIONS_PATH" --python_out="$PROTO_OUTPUT_PATH" assert_location.proto
protoc -I="$PROTO_DEFINITIONS_PATH" --python_out="$PROTO_OUTPUT_PATH" diagnostics.proto
protoc -I="$PROTO_DEFINITIONS_PATH" --python_out="$PROTO_OUTPUT_PATH" wifi_connect.proto
protoc -I="$PROTO_DEFINITIONS_PATH" --python_out="$PROTO_OUTPUT_PATH" wifi_remove.proto
protoc -I="$PROTO_DEFINITIONS_PATH" --python_out="$PROTO_OUTPUT_PATH" wifi_services.proto
