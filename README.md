# hm-config: Helium Miner Config Container

This repository contains the Dockerfile, basic scripts  and additional libraries required for the BTLE Application tool.
Github then builds the docker containers ready to be pushed to the Nebra Hotspots.
The base repository for the Python Application is in the subfolder config-python.

## Local development environment

Because the stack is tightly intertwined with Balena, the easiest way to test the code base on your own Raspberry Pi in your own Balena project.
The code has been developped and tested with the Raspberry Pi 3 B+. There are a few ways to build this app:

1. Cross-compile locally and deploy to Balena: `balena deploy hm-config --build` (preferred method)
2. Cross-compile locally only: `docker buildx build --platform linux/arm64 .`
3. ARM build on Balena: `git push balena YourLocalBranch:master` (deprecated)
4. Build directly on device with [local mode](https://www.balena.io/docs/learn/develop/local-mode/): `balena push local` (over 10 hours)

### Balena setup
* Create a new Balena project for Raspberry Pi 3 (64 Bit)
* Download and flash out the disk image provided and boot the device
* Add the remote Balena repo (`git remote add balena BALENA_USERNAME@git.balena-cloud.com:BALENA_USERNAME/BALENA_PROJECT.git`)
* The following ENV variables must be set: `FREQ`, `SENTRY_CONFIG`, `SENTRY_DIAG`, `SENTRY_PKTFWD`, and `VARIANT`