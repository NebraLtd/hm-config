from time import sleep

from lib.cputemp.bletools import BleTools

from gatewayconfig.logger import get_logger
from gatewayconfig.bluetooth.advertisements.bluetooth_connection_advertisement import BluetoothConnectionAdvertisement

logger = get_logger(__name__)
ADVERTISEMENT_TYPE = 'peripheral'
ADVERTISEMENT_INDEX = 0
ADVERTISEMENT_SECONDS = 300
ADVERTISEMENT_OFF_SLEEP_SECONDS = 5


class BluetoothAdvertisementProcessor:
    def __init__(self, eth0_mac_address, shared_state, variant_details):
        self.shared_state = shared_state
        self.connection_advertisement = BluetoothConnectionAdvertisement(ADVERTISEMENT_INDEX, eth0_mac_address,
                                                                         ADVERTISEMENT_TYPE, variant_details)

    def run(self):
        logger.debug("Running BluetoothAdvertisementProcessor")

        while True:
            if(self.shared_state.should_advertise_bluetooth is True):
                # Prepare to advertise by first scanning wifi and stopping any existing connections
                self.shared_state.should_advertise_bluetooth = False
                self.shared_state.should_scan_wifi = True
                try:
                    BleTools.disconnect_connections()
                except TypeError:
                    # Most Likely Already Disconnected
                    pass

                # Start advertising
                self.connection_advertisement.register()
                logger.debug("Starting Bluetooth advertisement")
                self.shared_state.is_advertising_bluetooth = True

                # Stop advertising
                sleep(ADVERTISEMENT_SECONDS)
                logger.debug("Stopping Bluetooth advertisement")
                self.connection_advertisement.unregister()
                self.shared_state.is_advertising_bluetooth = False
                self.shared_state.should_scan_wifi = False
            else:
                sleep(ADVERTISEMENT_OFF_SLEEP_SECONDS)
