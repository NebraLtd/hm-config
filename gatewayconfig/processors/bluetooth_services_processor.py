from lib.cputemp.service import Application
from gatewayconfig.bluetooth.services.device_information_service import DeviceInformationService
from gatewayconfig.bluetooth.services.helium_service import HeliumService

# Unlike the other processors, #run is not defined here. Instead, Application#run is used
class BluetoothServicesProcessor(Application):
    def __init__(self, eth0_mac_address, onboarding_key, pub_key, firmware_version, ethernet_is_online_filepath, shared_state):
        super().__init__()
        self.add_service(DeviceInformationService(0, eth0_mac_address))
        self.add_service(HeliumService(1, eth0_mac_address, onboarding_key, pub_key, firmware_version, ethernet_is_online_filepath, shared_state))
        self.register()
    