from lib.cputemp.advertisement import Advertisement

class BluetoothConnectionAdvertisement(Advertisement):
    # BLE advertisement
    def __init__(self, index):
        global variantDetails
        Advertisement.__init__(self, index, "peripheral")
        variant = variantDetails['APPNAME']
        macAddr = open("/sys/class/net/eth0/address").readline()\
            .strip().replace(":", "")[-6:].upper()
        localName = "Nebra %s Hotspot %s" % (variant, macAddr)
        self.add_local_name(localName)
        self.include_tx_power = True
        self.service_uuids = ["0fda92b2-44a2-4af2-84f5-fa682baa2b8d"]