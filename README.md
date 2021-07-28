# hm-config
Helium Miner Config Container

This repository contains the Dockerfile, basic scripts  and additional libraries required for the BTLE Application tool.

Github then builds the docker containers ready to be pushed to the Nebra Hotspots.

The base repository for the Python Application is in the subfolder config-python.

## Wheels
To resolve arm64 compiling with pip for now the repository includes arm64 wheels for the H3 Python library and the RPi.GPIO python library.

## Local development environment

**Note:** Right now the build process fails due to missing wheels.

Because the stack is tightly intertwined with Balena, the easiest way to test the code base on your own Raspberry Pi in your own Balena project.

* Create a new Balena project for Raspberry Pi 3 (64 Bit)
* Download and flash out the disk image provided and boot the device
* Add the remote Balena repo (`git remote add balena YourUser@git.balena-cloud.com:YourUser/YourProject.git`)

You can now push your changes using the following command:

```
$ git push balena YourLocalBranch:master
```


## Generating protobufs

Install protobuf, eg `sudo snap install protobuf` then run `genProtos.sh` from `src/protobuf`, eg: `cd src/protobuf && sh genProtos.sh`.