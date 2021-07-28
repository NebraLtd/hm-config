#!/bin/bash
protoc -I=protos/ --python_out=generated/ add_gateway.proto
protoc -I=protos/ --python_out=generated/ assert_location.proto
protoc -I=protos/ --python_out=generated/ diagnostics.proto
protoc -I=protos/ --python_out=generated/ wifi_connect.proto
protoc -I=protos/ --python_out=generated/ wifi_remove.proto
protoc -I=protos/ --python_out=generated/ wifi_services.proto
