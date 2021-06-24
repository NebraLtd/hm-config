#!/bin/bash
apt-get update -y
apt-get install dbus libusb-dev libdbus-1-dev libglib2.0-dev libudev-dev libical-dev libreadline-dev libgirepository1.0-dev python3-cairo-dev libcairo2 libcairo2-dev -y
apt-get install python3 python3-dev gcc cmake python3-pip -y
pip install -r requirements.txt
pip install -r test-requirements.txt
