# hm-config
Helium Miner Config Container

This repository contains the Dockerfile, basic scripts  and additional libraries required for the BTLE Application tool.

Github then builds the docker containers ready to be pushed to the Nebra Hotspots.

The base repository for the Python Application is at https://github.com/NebraLtd/helium-miner-config

## Wheels
To resolve arm64 compiling with pip for now the repository includes arm64 wheels for the H3 Python library and the RPi.GPIO python library.
