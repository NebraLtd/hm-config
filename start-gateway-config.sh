#!/usr/bin/env bash

# Disable BluetoothD on the host
# dbus-send --system --dest=org.freedesktop.systemd1 --type=method_call --print-reply /org/freedesktop/systemd1   org.freedesktop.systemd1.Manager.StopUnit string:"bluetooth.service" string:"replace"

#  sleep 1

# Start BluetoothD in container

# bluetoothd --experimental -C &

# sleep 1

# Advertise on channels 37, 38 and 39
echo 7 > /sys/kernel/debug/bluetooth/hci0/adv_channel_map
# Send a beacon every 152.5 ms
echo 153 > /sys/kernel/debug/bluetooth/hci0/adv_min_interval
echo 153 > /sys/kernel/debug/bluetooth/hci0/adv_max_interval

# Disable pairing

printf "pairable off\nquit" | /usr/bin/bluetoothctl

# Assuming this is being run within virtualenv, 
# `python` will refer to the correct variant
python config_program.py
