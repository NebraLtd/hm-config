from lib.cputemp.advertisement import Advertisement
from gatewayconfig.logger import get_logger
import gatewayconfig.constants as constants

logger = get_logger(__name__)


# BLE advertisement
class BluetoothConnectionAdvertisement(Advertisement):
    def __init__(self, index, eth0_mac_address, advertisement_type, variant_details):
        Advertisement.__init__(self, index, advertisement_type)
        logger.debug("Creating advertisement with MAC %s and variant details %s" % (eth0_mac_address, variant_details))
        # assumes eth0_mac_address already stripped and uppercase
        friendly_mac_address = eth0_mac_address.replace(":", "")[-6:]

        if 'APPNAME' in variant_details:
            friendly_variant = variant_details['APPNAME']
            advertisement_name = "Nebra %s Hotspot %s" % (friendly_variant, friendly_mac_address)
        else:
            friendly_variant = variant_details['FRIENDLY']
            advertisement_name = "%s %s" % (friendly_variant, friendly_mac_address)

        self.add_local_name(advertisement_name)
        self.include_tx_power = True
        self.service_uuids = [constants.HELIUM_SERVICE_UUID]
