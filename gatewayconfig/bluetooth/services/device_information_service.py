from lib.cputemp.service import Service
from gatewayconfig.bluetooth.characteristics.manufacturer_name_characteristic import ManufacturerNameCharacteristic
from gatewayconfig.bluetooth.characteristics.firmware_revision_characteristic import FirmwareRevisionCharacteristic
from gatewayconfig.bluetooth.characteristics.serial_number_characteristic import SerialNumberCharacteristic
import gatewayconfig.constants as constants


class DeviceInformationService(Service):
    # Service that provides basic information
    def __init__(self, index, eth0_mac_address):
        Service.__init__(self, index, constants.DEVINFO_SVC_UUID, True)
        self.add_characteristic(ManufacturerNameCharacteristic(self))
        self.add_characteristic(FirmwareRevisionCharacteristic(self))
        self.add_characteristic(SerialNumberCharacteristic(self, eth0_mac_address))
