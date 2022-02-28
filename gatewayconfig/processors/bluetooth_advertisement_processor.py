import threading

from lib.cputemp.bletools import BleTools

from gatewayconfig.logger import get_logger
from gatewayconfig.bluetooth.advertisements.bluetooth_connection_advertisement \
    import BluetoothConnectionAdvertisement

logger = get_logger(__name__)
ADVERTISEMENT_TYPE = 'peripheral'
ADVERTISEMENT_INDEX = 0
ADVERTISEMENT_SECONDS = 300
ADVERTISEMENT_OFF_SLEEP_SECONDS = 5


class BluetoothAdvertisementProcessor:
    def __init__(self, eth0_mac_address, shared_state, variant_details):
        self.shared_state = shared_state
        self.connection_advertisement = BluetoothConnectionAdvertisement(
            ADVERTISEMENT_INDEX, eth0_mac_address,
            ADVERTISEMENT_TYPE, variant_details)
        self.stop_advertisement_timer = None

    def start_advertisement(self):
        logger.debug("Starting Bluetooth advertisement")
        self.connection_advertisement.register()
        self.shared_state.is_advertising_bluetooth = True
        # for security, a start should always result in a scheduled stop
        self.schedule_stop_advertisement()

    def schedule_stop_advertisement(self, timer_seconds=ADVERTISEMENT_SECONDS):
        if self.stop_advertisement_timer:
            logger.debug("cancelling existing stop advertisement timer")
            self.stop_advertisement_timer.cancel()

        # trigger the time to stop advertisement
        self.stop_advertisement_timer = threading.Timer(
            timer_seconds, self.stop_advertisement)
        self.stop_advertisement_timer.start()
        logger.debug('scheduled stop advertisement in %s seconds', timer_seconds)

    def stop_advertisement(self):
        logger.debug("Stopping Bluetooth advertisement")
        self.connection_advertisement.unregister()
        self.shared_state.is_advertising_bluetooth = False
        self.shared_state.should_scan_wifi = False

    def run(self):
        logger.debug("Running BluetoothAdvertisementProcessor")

        while True:
            advertise_event = self.shared_state.should_advertise_bluetooth_condition_event.wait()
            if advertise_event:
                # Prepare to advertise by first scanning wifi and stopping any existing connections
                self.shared_state.should_scan_wifi = True
                try:
                    BleTools.disconnect_connections()
                except TypeError:
                    # Most Likely Already Disconnected
                    pass

                # Start advertising
                self.start_advertisement()

                # clear the event
                self.shared_state.should_advertise_bluetooth_condition_event.clear()
