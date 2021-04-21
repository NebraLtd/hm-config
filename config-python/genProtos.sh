#!/bin/bash
protoc -I=protos/ --python_out=. add_gateway.proto
protoc -I=protos/ --python_out=. assert_location.proto
protoc -I=protos/ --python_out=. diagnostics.proto
protoc -I=protos/ --python_out=. wifi_connect.proto
protoc -I=protos/ --python_out=. wifi_remove.proto
protoc -I=protos/ --python_out=. wifi_services.proto
