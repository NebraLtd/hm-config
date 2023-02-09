#! /bin/bash

# Wait for the diagnostics app to be loaded
until wget -q -T 10 -O - http://localhost/json > /dev/null 2>&1
do
    echo "Diagnostics container not ready. Going to sleep."
    sleep 10
done

# Load dbus-wait script
# shellcheck source=/dev/null
source /opt/nebra/dbus-wait.sh

# Advertise on channels 37, 38 and 39
echo 7 > /sys/kernel/debug/bluetooth/hci0/adv_channel_map
# Send a beacon every 153 x 0.625ms = 95.625ms (244 is 152.5ms)
echo 153 > /sys/kernel/debug/bluetooth/hci0/adv_min_interval
echo 153 > /sys/kernel/debug/bluetooth/hci0/adv_max_interval

# Disable pairing
printf "pairable off\nquit" | /usr/bin/bluetoothctl

# Load setenv script
# shellcheck source=/dev/null
source /opt/nebra/setenv.sh

prevent_start="${PREVENT_START_GATEWAYCONFIG:-0}"
if [ "$prevent_start" = 1 ]; then
    echo "gatewayconfig will not be started. PREVENT_START_GATEWAYCONFIG=1"
    while true; do sleep 1000; done
else
	# Check dbus container is ready and then launch config
    wait_for_dbus \
        && python gatewayconfig
fi
