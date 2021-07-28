#!/bin/bash
protoc -I=protobuf/protos/ --python_out=. protobuf/generated/add_gateway.proto
protoc -I=protobuf/protos/ --python_out=. protobuf/generated/assert_location.proto
protoc -I=protobuf/protos/ --python_out=. protobuf/generated/diagnostics.proto
protoc -I=protobuf/protos/ --python_out=. protobuf/generated/wifi_connect.proto
protoc -I=protobuf/protos/ --python_out=. protobuf/generated/wifi_remove.proto
protoc -I=protobuf/protos/ --python_out=. protobuf/generated/wifi_services.proto
