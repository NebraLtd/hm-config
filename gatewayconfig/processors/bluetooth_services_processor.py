from lib.cputemp.service import Application
from gatewayconfig.bluetooth.services.device_information_service import DeviceInformationService
from gatewayconfig.bluetooth.services.helium_service import HeliumService
from gatewayconfig.logger import get_logger

logger = get_logger(__name__)


class BluetoothServicesProcessor(Application):
    def __init__(self, eth0_mac_address, wlan0_mac_address, firmware_version,
                 ethernet_is_online_filepath, shared_state):
        super().__init__()
        self.add_service(DeviceInformationService(0, eth0_mac_address))
        self.add_service(HeliumService(1, eth0_mac_address, wlan0_mac_address, firmware_version,
                         ethernet_is_online_filepath, shared_state))
        self.register()

    # Unlike the other processors, #run is not defined here. Instead, Application#run is used
    def run(self):
        try:
            super().run()
        except Exception:
            logger.exception("BluetoothServicesProcessor #run failed for an unknown reason.")
