from lib.cputemp.service import Service

from gatewayconfig.bluetooth.characteristics.onboarding_key_characteristic import OnboardingKeyCharacteristic
from gatewayconfig.bluetooth.characteristics.public_key_characteristic import PublicKeyCharacteristic
from gatewayconfig.bluetooth.characteristics.wifi_services_characteristic import WifiServicesCharacteristic
from gatewayconfig.bluetooth.characteristics.wifi_configured_services_characteristic import WifiConfiguredServicesCharacteristic
from gatewayconfig.bluetooth.characteristics.diagnostics_characteristic import DiagnosticsCharacteristic
from gatewayconfig.bluetooth.characteristics.mac_address_characteristic import MacAddressCharacteristic
from gatewayconfig.bluetooth.characteristics.lights_characteristic import LightsCharacteristic
from gatewayconfig.bluetooth.characteristics.wifi_ssid_characteristic import WifiSSIDCharacteristic
from gatewayconfig.bluetooth.characteristics.assert_location_characteristic import AssertLocationCharacteristic
from gatewayconfig.bluetooth.characteristics.add_gateway_characteristic import AddGatewayCharacteristic
from gatewayconfig.bluetooth.characteristics.wifi_connect_characteristic import WifiConnectCharacteristic
from gatewayconfig.bluetooth.characteristics.ethernet_online_characteristic import EthernetOnlineCharacteristic
from gatewayconfig.bluetooth.characteristics.software_version_characteristic import SoftwareVersionCharacteristic
from gatewayconfig.bluetooth.characteristics.wifi_remove_characteristic import WifiRemoveCharacteristic

class HeliumService(Service):
    DEVINFO_SVC_UUID = "0fda92b2-44a2-4af2-84f5-fa682baa2b8d"

    def __init__(self, index):

        Service.__init__(self, index, self.DEVINFO_SVC_UUID, True)
        self.add_characteristic(OnboardingKeyCharacteristic(self))
        self.add_characteristic(PublicKeyCharacteristic(self))
        self.add_characteristic(WifiServicesCharacteristic(self))
        self.add_characteristic(WifiConfiguredServicesCharacteristic(self))
        self.add_characteristic(DiagnosticsCharacteristic(self))
        self.add_characteristic(MacAddressCharacteristic(self))
        self.add_characteristic(LightsCharacteristic(self))
        self.add_characteristic(WifiSSIDCharacteristic(self))
        self.add_characteristic(AssertLocationCharacteristic(self))
        self.add_characteristic(AddGatewayCharacteristic(self))
        self.add_characteristic(WifiConnectCharacteristic(self))
        self.add_characteristic(EthernetOnlineCharacteristic(self))
        self.add_characteristic(SoftwareVersionCharacteristic(self))
        self.add_characteristic(WifiRemoveCharacteristic(self))