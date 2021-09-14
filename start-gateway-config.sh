#!/usr/bin/env bash

source dbus-wait.sh

./systemd-stop-unit.sh bluetooth.service

rfkill block bluetooth && rfkill unblock bluetooth
wait_for_dbus \
	&& /usr/lib/bluetooth/bluetoothd  --nodetach

# Advertise on channels 37, 38 and 39
echo 7 > /sys/kernel/debug/bluetooth/hci0/adv_channel_map
# Send a beacon every 152.5 ms
echo 153 > /sys/kernel/debug/bluetooth/hci0/adv_min_interval
echo 153 > /sys/kernel/debug/bluetooth/hci0/adv_max_interval

# Disable pairing

printf "pairable off\nquit" | /usr/bin/bluetoothctl

python gatewayconfig
