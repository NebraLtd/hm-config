#!/usr/bin/env sh

. ./dbus-wait.sh

# Advertise on channels 37, 38 and 39
echo 7 > /sys/kernel/debug/bluetooth/hci0/adv_channel_map
# Send a beacon every 152.5 ms
echo 153 > /sys/kernel/debug/bluetooth/hci0/adv_min_interval
echo 153 > /sys/kernel/debug/bluetooth/hci0/adv_max_interval

# Disable pairing

printf "pairable off\nquit" | /usr/bin/bluetoothctl

wait_for_dbus \
	&& python gatewayconfig
