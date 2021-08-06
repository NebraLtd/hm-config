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

### Setting up Python on Ubuntu

These are optional instructions to have an Ubuntu environment closely mimic production.

1. Install pyenv: `curl https://pyenv.run | bash`
2. Install Python 3.7.3 dependency: 

```
sudo apt-get install -y libffi-dev libssl-dev make build-essential libssl-dev zlib1g-dev libbz2-dev \
    libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
    xz-utils tk-dev libffi-dev liblzma-dev python-openssl git \
     libdbus-glib-1-dev libgirepository1.0-dev python3-gi bluez
```
3. Install Python 3.7.3: `pyenv install 3.7.3 && pyenv local 3.7.3`
4. Check correctly installed: `python -V`
5. Setup virtualenv: `python3 -m venv venv && source venv/bin/activate`
6. Install dependencies: `pip install -r requirements.txt`

## Generating protobufs

Install protobuf, eg `sudo snap install protobuf` then run `genProtos.sh` from `src/protobuf`, eg: `cd src/protobuf && sh genProtos.sh`.
