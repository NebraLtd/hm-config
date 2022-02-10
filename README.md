# hm-config: Helium Miner Config Container

This repository contains the Dockerfile, basic scripts  and additional libraries required for the BTLE Application tool.
[helium/gateway-config](https://github.com/helium/gateway-config) is the upstream repo that this is built against.

Directory layout:

- `.github/`: Github workflows and other settings.
- `example/`: Files that are examples of what will be loaded on an actual hotspot. These files are especially useful for testing without a full hotspot.
- `gatewayconfig/`: The main Python application.
- `lib/`: Python files copied from other reposittories.
- `protos/`: Protobuf definitions. Generated protos go to `gatewayconfig/protos/` by default.
- `tests/`: Test files.

## Local development environment

Running locally:

```
PYTHONPATH=./ MINER_KEYS_FILEPATH=./example/onboarding_key.txt ETH0_MAC_ADDRESS_PATH=./example/eth0_mac_address.txt python minerconfig
```

Because the stack is tightly intertwined with Balena, the easiest way to test the code base on your own Raspberry Pi in your own Balena project.
The code has been developped and tested with the Raspberry Pi 3 B+. There are a few ways to build this app:

1. Cross-compile locally and deploy to Balena: `balena deploy dev-XXX --build` (preferred method)
2. Cross-compile locally only: `docker buildx build --platform linux/arm64 .`
3. ARM build on Balena: `git push balena YourLocalBranch:master` (deprecated)
4. Build directly on device with [local mode](https://www.balena.io/docs/learn/develop/local-mode/): `balena push local` (over 10 hours)


```
balena deploy hm-diag --build --debug
```

### Balena setup
* Create a new Balena project for Raspberry Pi 3 (64 Bit)
* Download and flash out the disk image provided and boot the device
* Add the remote Balena repo (`git remote add balena BALENA_USERNAME@git.balena-cloud.com:BALENA_USERNAME/BALENA_PROJECT.git`)
* The following ENV variables must be set: `FREQ`, `SENTRY_CONFIG`, `SENTRY_DIAG`, `SENTRY_PKTFWD`, and `VARIANT`
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
6. Install python `wheel` package: `python3 -m pip install wheel`
7. Install dependencies: `pip install -r requirements.txt`

## Testing

Assuming virtualenv has been activated, execute the following command to run the tests:

```
pip install -r test-requirements.txt
pytest
# Or test and run coverage report
PYTHONPATH=./ pytest --cov=minerconfig --cov=lib
```

## Generating protobufs

- Install protobuf
    - Ubuntu: `sudo snap install protobuf`
    - Mac: `brew install protobuf`
- Run `generate-protos.sh`
    - `cd protos && sh generate-protos.sh`

## Pre built containers

This repo automatically builds docker containers and uploads them to two repositories for easy access:
- [hm-config on DockerHub](https://hub.docker.com/r/nebraltd/hm-config)
- [hm-config on GitHub Packages](https://github.com/NebraLtd/hm-config/pkgs/container/hm-config)

The images are tagged using the docker long and short commit SHAs for that release. The current version deployed to miners can be found in the [helium-miner-software repo](https://github.com/NebraLtd/helium-miner-software/blob/production/docker-compose.yml).
