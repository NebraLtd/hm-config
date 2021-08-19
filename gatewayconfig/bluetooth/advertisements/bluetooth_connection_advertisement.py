from lib.cputemp.advertisement import Advertisement

ADVERTISEMENT_SERVICE_UUID = "0fda92b2-44a2-4af2-84f5-fa682baa2b8d"
UNKNOWN_MAC_ADDRESS_VAL = "XXXXXX"

# BLE advertisement
class BluetoothConnectionAdvertisement(Advertisement):
    def __init__(self, index, eth0_mac_address, advertisement_type, variant):
        Advertisement.__init__(self, index, advertisement_type)
        try:
            mac_address_last6 = eth0_mac_address.replace(":", "")[-6:] 

        except FileNotFoundError:
            mac_address_last6 = UNKNOWN_MAC_ADDRESS_VAL

        advertisement_name = "Nebra %s Hotspot (%s)" % (mac_address_last6, variant)
        self.add_local_name(advertisement_name)
        self.include_tx_power = True
        self.service_uuids = [ADVERTISEMENT_SERVICE_UUID]