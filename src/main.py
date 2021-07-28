#!/usr/bin/python3

import os
import sentry_sdk
import dbus
import logging
import sys
import json
import nmcli_custom as nmcli
import uuids
import h3

import threading
# From imports
from time import sleep
from RPi import GPIO
from variant_definitions import variant_definitions

# BLE Library
from lib.advertisement import Advertisement
from lib.service import Application, Service, Characteristic, Descriptor
from lib.bletools import BleTools

# Protobuf Imports
import protobuf.generated.add_gateway_pb2
import protobuf.generated.assert_location_pb2
import protobuf.generated.diagnostics_pb2
import protobuf.generated.wifi_connect_pb2
import protobuf.generated.wifi_remove_pb2
import protobuf.generated.wifi_services_pb2

from gpiozero import Button, LED

# ET Phone Home
variant = os.getenv('VARIANT')
sentry_key = os.getenv('SENTRY_CONFIG')
balena_id = os.getenv('BALENA_DEVICE_UUID')
balena_app = os.getenv('BALENA_APP_NAME')
uuids.FIRMWARE_VERSION = os.getenv('FIRMWARE_VERSION')
sentry_sdk.init(sentry_key, environment=balena_app)
sentry_sdk.set_user({"id": balena_id})
sentry_sdk.set_context("variant", {variant})

variantDetails = variant_definitions[variant]

# Disable sudo for nmcli
nmcli.disable_use_sudo()


GATT_CHRC_IFACE = "org.bluez.GattCharacteristic1"
NOTIFY_TIMEOUT = 5000

# Public Onboarding Keys
while True:
    try:
        public_keys_file = open("/var/data/public_keys").readline().split('"')
        break
    except FileNotFoundError:
        logging.debug('Waiting for keyfile')
    sleep(60)

# Keyfile exists, now running.
pubKey = str(public_keys_file[1])
onboardingKey = str(public_keys_file[3])
animalName = str(public_keys_file[5])

# Setup Thread Variables
advertisementLED = False
diagnosticsStatus = False
scanWifi = False
wifiCache = []

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)


class ConfigAdvertisement(Advertisement):
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


class DeviceInformationService(Service):
    # Service that provides basic information
    def __init__(self, index):
        Service.__init__(self, index, uuids.DEVINFO_SVC_UUID, True)
        self.add_characteristic(ManufactureNameCharacteristic(self))
        self.add_characteristic(FirmwareRevisionCharacteristic(self))
        self.add_characteristic(SerialNumberCharacteristic(self))


class ManufactureNameCharacteristic(Characteristic):
    def __init__(self, service):
        Characteristic.__init__(
                self, uuids.MANUFACTURE_NAME_CHARACTERISTIC_UUID,
                ["read"], service)

    def ReadValue(self, options):
        logging.debug('Read Manufacturer')
        value = []
        val = "Nebra LTD."
        for c in val:
            value.append(dbus.Byte(c.encode()))
        return value


class FirmwareRevisionCharacteristic(Characteristic):
    def __init__(self, service):
        Characteristic.__init__(
                self, uuids.FIRMWARE_REVISION_CHARACTERISTIC_UUID,
                ["read"], service)

    def ReadValue(self, options):
        logging.debug('Read Firmware')

        val = os.getenv('FIRMWARE_VERSION')
        value = []

        for c in val:
            value.append(dbus.Byte(c.encode()))

        return value


class SerialNumberCharacteristic(Characteristic):

    def __init__(self, service):
        Characteristic.__init__(
                self, uuids.SERIAL_NUMBER_CHARACTERISTIC_UUID,
                ["read"], service)

    def ReadValue(self, options):
        logging.debug('Read Serial Number')
        value = []
        val = open("/sys/class/net/eth0/address").readline() \
            .strip().replace(":", "")

        for c in val:
            value.append(dbus.Byte(c.encode()))
        return value


class HeliumService(Service):
    DEVINFO_SVC_UUID = "0fda92b2-44a2-4af2-84f5-fa682baa2b8d"

    def __init__(self, index):

        Service.__init__(self, index, self.DEVINFO_SVC_UUID, True)
        self.add_characteristic(OnboardingKeyCharacteristic(self))
        self.add_characteristic(PublicKeyCharacteristic(self))
        self.add_characteristic(WiFiServicesCharacteristic(self))
        self.add_characteristic(WiFiConfiguredServicesCharacteristic(self))
        self.add_characteristic(DiagnosticsCharacteristic(self))
        self.add_characteristic(MacAddressCharacteristic(self))
        self.add_characteristic(LightsCharacteristic(self))
        self.add_characteristic(WiFiSSIDCharacteristic(self))
        self.add_characteristic(AssertLocationCharacteristic(self))
        self.add_characteristic(AddGatewayCharacteristic(self))
        self.add_characteristic(WiFiConnectCharacteristic(self))
        self.add_characteristic(EthernetOnlineCharacteristic(self))
        self.add_characteristic(SoftwareVersionCharacteristic(self))
        self.add_characteristic(WiFiRemoveCharacteristic(self))


class OnboardingKeyCharacteristic(Characteristic):
    def __init__(self, service):
        Characteristic.__init__(
                self, uuids.ONBOARDING_KEY_CHARACTERISTIC_UUID,
                ["read"], service)
        self.add_descriptor(OnboardingKeyDescriptor(self))
        self.add_descriptor(utf8Format(self))

    def ReadValue(self, options):
        logging.debug('Read Onboarding Key')
        value = []
        val = onboardingKey

        for c in val:
            value.append(dbus.Byte(c.encode()))
        return value


class OnboardingKeyDescriptor(Descriptor):

    def __init__(self, characteristic):
        Descriptor.__init__(
                self, uuids.USER_DESC_DESCRIPTOR_UUID,
                ["read"],
                characteristic)

    def ReadValue(self, options):
        value = []
        desc = uuids.ONBOARDING_KEY_VALUE

        for c in desc:
            value.append(dbus.Byte(c.encode()))
        return value


class PublicKeyCharacteristic(Characteristic):

    def __init__(self, service):
        Characteristic.__init__(
                self, uuids.PUBLIC_KEY_CHARACTERISTIC_UUID,
                ["read"], service)
        self.add_descriptor(PublicKeyDescriptor(self))
        self.add_descriptor(utf8Format(self))

    def ReadValue(self, options):
        logging.debug('Read Public Key')
        value = []
        val = pubKey
        for c in val:
            value.append(dbus.Byte(c.encode()))
        return value


class PublicKeyDescriptor(Descriptor):

    def __init__(self, characteristic):
        Descriptor.__init__(
                self, uuids.USER_DESC_DESCRIPTOR_UUID,
                ["read"],
                characteristic)

    def ReadValue(self, options):
        value = []
        desc = uuids.PUBLIC_KEY_VALUE

        for c in desc:
            value.append(dbus.Byte(c.encode()))
        return value


class WiFiServicesCharacteristic(Characteristic):

    global wifiCache

    def __init__(self, service):
        Characteristic.__init__(
                self, uuids.WIFI_SERVICES_CHARACTERISTIC_UUID,
                ["read"], service)
        self.add_descriptor(WiFiServicesDescriptor(self))
        self.add_descriptor(opaqueStructure(self))

    def ReadValue(self, options):
        logging.debug('Read WiFi Services')
        wifiSsids = wifi_services_pb2.wifi_services_v1()

        for network in wifiCache:
            ssidStr = str(network.ssid)
            if(ssidStr != "--" and ssidStr != ""):
                if(ssidStr not in wifiSsids.services):
                    wifiSsids.services.append(ssidStr)
                    logging.debug(ssidStr)
        value = []
        val = wifiSsids.SerializeToString()

        for c in val:
            value.append(dbus.Byte(c))
        if("offset" in options):
            cutDownArray = value[int(options["offset"]):]
            return cutDownArray
        else:
            return value


class WiFiServicesDescriptor(Descriptor):

    def __init__(self, characteristic):
        Descriptor.__init__(
                self, uuids.USER_DESC_DESCRIPTOR_UUID,
                ["read"],
                characteristic)

    def ReadValue(self, options):
        value = []
        desc = uuids.WIFI_SERVICES_VALUE

        for c in desc:
            value.append(dbus.Byte(c.encode()))
        return value


class WiFiConfiguredServicesCharacteristic(Characteristic):

    global wifiCache

    def __init__(self, service):
        Characteristic.__init__(
                self, uuids.WIFI_CONFIGURED_SERVICES_CHARACTERISTIC_UUID,
                ["read"], service)
        self.add_descriptor(WiFiConfiguredServicesDescriptor(self))
        self.add_descriptor(opaqueStructure(self))

    def ReadValue(self, options):
        logging.debug('Read WiFi CONFIGURED Services')
        wifiConfigured = wifi_services_pb2.wifi_services_v1()

        for network in wifiCache:
            if(network.ssid != "--"):
                if(network.in_use):
                    activeConnection = str(network.ssid)
                    wifiConfigured.services.append(activeConnection)
                    print(activeConnection)
        value = []
        val = wifiConfigured.SerializeToString()

        for c in val:
            value.append(dbus.Byte(c))

        return value


class WiFiConfiguredServicesDescriptor(Descriptor):

    def __init__(self, characteristic):
        Descriptor.__init__(
                self, uuids.USER_DESC_DESCRIPTOR_UUID,
                ["read"],
                characteristic)

    def ReadValue(self, options):
        value = []
        desc = uuids.WIFI_CONFIGURED_SERVICES_VALUE

        for c in desc:
            value.append(dbus.Byte(c.encode()))
        return value


class DiagnosticsCharacteristic(Characteristic):
    # Returns proto of eth, wifi, fw, ip, p2pstatus

    def __init__(self, service):
        Characteristic.__init__(
                self, uuids.DIAGNOSTICS_CHARACTERISTIC_UUID,
                ["read"], service)
        self.add_descriptor(DiagnosticsDescriptor(self))
        self.add_descriptor(opaqueStructure(self))
        self.p2pstatus = ""

    def ReadValue(self, options): # noqa 901
        # TODO (Rob): come back and make this method less complex for
        # C901 complexity rules.
        logging.debug('Read diagnostics')
        logging.debug('Diagnostics miner_bus')
        miner_bus = dbus.SystemBus()
        logging.debug('Diagnostics miner_object')
        miner_object = miner_bus.get_object('com.helium.Miner', '/')
        logging.debug('Diagnostics miner_interface')
        miner_interface = dbus.Interface(miner_object, 'com.helium.Miner')
        logging.debug('Diagnostics p2pstatus')
        try:
            self.p2pstatus = miner_interface.P2PStatus()
            logging.debug('DBUS P2P SUCCEED')
            logging.debug(self.p2pstatus)
        except dbus.exceptions.DBusException:
            self.p2pstatus = ""
            logging.debug('DBUS P2P FAIL')

        try:
            ethIP = nmcli.device.show('eth0')['IP4.ADDRESS[1]'][:-3]
        except KeyError:
            pass
        try:
            wlanIP = nmcli.device.show('wlan0')['IP4.ADDRESS[1]'][:-3]
        except KeyError:
            pass

        ipAddress = "0.0.0.0"  # nosec
        if('ethIP' in locals()):
            ipAddress = str(ethIP)
        elif('wlanIP' in locals()):
            ipAddress = str(wlanIP)

        diagnosticsProto = diagnostics_pb2.diagnostics_v1()
        diagnosticsProto.diagnostics['connected'] = str(self.p2pstatus[0][1])
        diagnosticsProto.diagnostics['dialable'] = str(self.p2pstatus[1][1])
        diagnosticsProto.diagnostics['height'] = str(self.p2pstatus[3][1])
        diagnosticsProto.diagnostics['nat_type'] = str(self.p2pstatus[2][1])
        try:
            diagnosticsProto.diagnostics['eth'] = \
                open("/sys/class/net/eth0/address").readline(). \
                strip().replace(":", "")
        except FileNotFoundError:
            diagnosticsProto.diagnostics['eth'] = "FF:FF:FF:FF:FF:FF"
        diagnosticsProto.diagnostics['fw'] = os.getenv('FIRMWARE_VERSION')
        diagnosticsProto.diagnostics['ip'] = ipAddress
        try:
            wifi_diag = open("/sys/class/net/wlan0/address").readline(). \
                strip().replace(":", "")
            diagnosticsProto.diagnostics['wifi'] = wifi_diag
        except FileNotFoundError:
            diagnosticsProto.diagnostics['wifi'] = "FF:FF:FF:FF:FF:FF"
        logging.debug('items added to proto')
        value = []
        val = diagnosticsProto.SerializeToString()
        logging.debug(val)
        for c in val:
            value.append(dbus.Byte(c))
        return value


class DiagnosticsDescriptor(Descriptor):

    def __init__(self, characteristic):
        Descriptor.__init__(
                self, uuids.USER_DESC_DESCRIPTOR_UUID,
                ["read"],
                characteristic)

    def ReadValue(self, options):
        value = []
        desc = uuids.DIAGNOSTICS_VALUE
        for c in desc:
            value.append(dbus.Byte(c.encode()))
        return value


class MacAddressCharacteristic(Characteristic):

    def __init__(self, service):
        Characteristic.__init__(
                self, uuids.MAC_ADDRESS_CHARACTERISTIC_UUID,
                ["read"], service)
        self.add_descriptor(MacAddressDescriptor(self))
        self.add_descriptor(utf8Format(self))

    def ReadValue(self, options):
        logging.debug('Read Mac Address')
        value = []
        val = open("/sys/class/net/eth0/address").readline().strip() \
            .replace(":", "")

        for c in val:
            value.append(dbus.Byte(c.encode()))
        return value


class MacAddressDescriptor(Descriptor):

    def __init__(self, characteristic):
        Descriptor.__init__(
                self, uuids.USER_DESC_DESCRIPTOR_UUID,
                ["read"],
                characteristic)

    def ReadValue(self, options):
        value = []
        desc = uuids.MAC_ADDRESS_VALUE

        for c in desc:
            value.append(dbus.Byte(c.encode()))
        return value


class LightsCharacteristic(Characteristic):

    def __init__(self, service):
        Characteristic.__init__(
                self, uuids.LIGHTS_CHARACTERISTIC_UUID,
                ["read"], service)
        self.add_descriptor(LightsDescriptor(self))
        self.add_descriptor(utf8Format(self))

    def ReadValue(self, options):
        logging.debug('Read Lights')
        value = []
        val = "false"

        for c in val:
            value.append(dbus.Byte(c.encode()))
        return value


class LightsDescriptor(Descriptor):

    def __init__(self, characteristic):
        Descriptor.__init__(
                self, uuids.USER_DESC_DESCRIPTOR_UUID,
                ["read"],
                characteristic)

    def ReadValue(self, options):
        value = []
        desc = uuids.LIGHTS_VALUE

        for c in desc:
            value.append(dbus.Byte(c.encode()))
        return value


class WiFiSSIDCharacteristic(Characteristic):

    global wifiCache

    def __init__(self, service):
        Characteristic.__init__(
                self, uuids.WIFI_SSID_CHARACTERISTIC_UUID,
                ["read"], service)
        self.add_descriptor(WiFiSSIDDescriptor(self))
        self.add_descriptor(utf8Format(self))

    def ReadValue(self, options):

        logging.debug('Read WiFi SSID')
        activeConnection = ""
        for network in wifiCache:
            if(network.ssid != "--"):
                if(network.in_use):
                    activeConnection = str(network.ssid)
                    print(activeConnection)
        value = []

        for c in activeConnection:
            value.append(dbus.Byte(c.encode()))
        return value


class WiFiSSIDDescriptor(Descriptor):

    def __init__(self, characteristic):
        Descriptor.__init__(
                self, uuids.USER_DESC_DESCRIPTOR_UUID,
                ["read"],
                characteristic)

    def ReadValue(self, options):

        value = []
        desc = uuids.WIFI_SSID_VALUE

        for c in desc:
            value.append(dbus.Byte(c.encode()))
        return value


class AssertLocationCharacteristic(Characteristic):

    def __init__(self, service):
        Characteristic.__init__(
                self, uuids.ASSERT_LOCATION_CHARACTERISTIC_UUID,
                ["read", "write", "notify"], service)
        self.add_descriptor(AssertLocationDescriptor(self))
        self.add_descriptor(opaqueStructure(self))
        self.notifyValue = []
        for c in "init":
            self.notifyValue.append(dbus.Byte(c.encode()))

    def AddGatewayCallback(self):
        if self.notifying:
            logging.debug('Callback Assert Location')
            value = []
            val = ""

            for c in val:
                value.append(dbus.Byte(c.encode()))
            self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": value}, [])

    def StartNotify(self):

        logging.debug('Notify Assert Location')
        if self.notifying:
            return

        self.notifying = True

        self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": self.notifyValue},
                               [])
        self.add_timeout(30000, self.AddGatewayCallback)

    def StopNotify(self):
        self.notifying = False

    def WriteValue(self, value, options):
        logging.debug('Write Assert Location')
        logging.debug(value)
        assLocDet = assert_location_pb2.assert_loc_v1()
        logging.debug('PB2C')
        assLocDet.ParseFromString(bytes(value))
        logging.debug('PB2P')
        logging.debug(str(assLocDet))
        miner_bus = dbus.SystemBus()
        miner_object = miner_bus.get_object('com.helium.Miner', '/')
        sleep(0.05)
        miner_interface = dbus.Interface(miner_object, 'com.helium.Miner')
        sleep(0.05)
        h3String = h3.geo_to_h3(assLocDet.lat, assLocDet.lon, 12)
        # logging.debug(h3String)
        # H3String, Owner, Nonce, Amount, Fee, Paye
        minerAssertRequest = \
            miner_interface. \
            AssertLocation(h3String,
                           assLocDet.owner, assLocDet.nonce, assLocDet.amount,
                           assLocDet.fee, assLocDet.payer)
        # logging.debug(assLocDet)
        self.notifyValue = minerAssertRequest

    def ReadValue(self, options):
        logging.debug('Read Assert Location')
        # logging.debug(options)
        if("offset" in options):
            cutDownArray = self.notifyValue[int(options["offset"]):]
            return cutDownArray
        else:
            return self.notifyValue


class AssertLocationDescriptor(Descriptor):

    def __init__(self, characteristic):
        Descriptor.__init__(
                self, uuids.USER_DESC_DESCRIPTOR_UUID,
                ["read"],
                characteristic)

    def ReadValue(self, options):
        value = []
        desc = uuids.ASSERT_LOCATION_VALUE

        for c in desc:
            value.append(dbus.Byte(c.encode()))
        return value


class AddGatewayCharacteristic(Characteristic):

    def __init__(self, service):
        Characteristic.__init__(
                self, uuids.ADD_GATEWAY_CHARACTERISTIC_UUID,
                ["read", "write", "notify"], service)
        self.add_descriptor(AddGatewayDescriptor(self))
        self.add_descriptor(opaqueStructure(self))
        self.notifyValue = []
        for c in "init":
            self.notifyValue.append(dbus.Byte(c.encode()))

    def AddGatewayCallback(self):
        if self.notifying:
            logging.debug('Callback Add Gateway')
            # value = []
            # val = ""

            # for c in val:
            #    value.append(dbus.Byte(c.encode()))
            self.PropertiesChanged(GATT_CHRC_IFACE,
                                   {"Value": self.notifyValue}, [])

    def StartNotify(self):

        logging.debug('Notify Add Gateway')
        if self.notifying:
            return

        self.notifying = True

        self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": self.notifyValue},
                               [])
        self.add_timeout(30000, self.AddGatewayCallback)

    def StopNotify(self):
        self.notifying = False

    def WriteValue(self, value, options):
        logging.debug('Write Add Gateway')
        waitVal = []
        for c in "wait":
            waitVal.append(dbus.Byte(c.encode()))
        self.notifyValue = waitVal

        # logging.debug(value)
        addGatewayDetails = add_gateway_pb2.add_gateway_v1()
        # logging.debug('PB2C')
        addGatewayDetails.ParseFromString(bytes(value))
        # logging.debug('PB2P')
        # logging.debug(str(addGatewayDetails))
        miner_bus = dbus.SystemBus()
        miner_object = miner_bus.get_object('com.helium.Miner', '/')
        sleep(0.05)
        miner_interface = dbus.Interface(miner_object, 'com.helium.Miner')
        sleep(0.05)
        addMinerRequest = \
            miner_interface. \
            AddGateway(addGatewayDetails.owner, addGatewayDetails.fee,
                       addGatewayDetails.amount, addGatewayDetails.payer)
        # logging.debug(addMinerRequest)
        logging.debug("Adding Response")
        self.notifyValue = addMinerRequest

    def ReadValue(self, options):
        logging.debug('Read Add Gateway')
        if("offset" in options):
            cutDownArray = self.notifyValue[int(options["offset"]):]
            return cutDownArray
        else:
            return self.notifyValue
        # logging.debug(self.notifyValue)


class AddGatewayDescriptor(Descriptor):

    def __init__(self, characteristic):
        Descriptor.__init__(
                self, uuids.USER_DESC_DESCRIPTOR_UUID,
                ["read"],
                characteristic)

    def ReadValue(self, options):
        value = []
        desc = uuids.ADD_GATEWAY_KEY_VALUE

        for c in desc:
            value.append(dbus.Byte(c.encode()))
        return value


class WiFiConnectCharacteristic(Characteristic):

    def __init__(self, service):
        self.notifying = False
        Characteristic.__init__(
                self, uuids.WIFI_CONNECT_CHARACTERISTIC_UUID,
                ["read", "write", "notify"], service)
        self.add_descriptor(WiFiConnectDescriptor(self))
        self.add_descriptor(opaqueStructure(self))
        self.WiFiStatus = ""

    def WiFiConnectCallback(self):
        if self.notifying:
            logging.debug('Callback WiFi Connect')
            value = []
            self.WiFiStatus = "timeout"

            for c in self.WiFiStatus:
                value.append(dbus.Byte(c.encode()))
            self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": value}, [])

        return self.notifying

    def StartNotify(self):

        logging.debug('Notify WiFi Connect')
        if self.notifying:
            return

        self.notifying = True

        value = []
        self.WiFiStatus = self.checkWiFIStatus()
        for c in self.WiFiStatus:
            value.append(dbus.Byte(c.encode()))
        self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": value}, [])
        self.add_timeout(30000, self.WiFiConnectCallback)

    def StopNotify(self):
        self.notifying = False

    def WriteValue(self, value, options):
        logging.debug('Write WiFi Connect')
        if(self.checkWiFIStatus() == "connected"):
            nmcli.device.disconnect('wlan0')
            logging.debug('Disconnected From Wifi')
        # logging.debug(value)
        wiFiDetails = wifi_connect_pb2.wifi_connect_v1()
        # logging.debug('PB2C')
        wiFiDetails.ParseFromString(bytes(value))
        # logging.debug('PB2P')
        self.WiFiStatus = "already"
        logging.debug(str(wiFiDetails.service))

        nmcli.device.wifi_connect(str(wiFiDetails.service),
                                  str(wiFiDetails.password))
        self.WiFiStatus = self.checkWiFIStatus()

    def checkWiFIStatus(self):
        # Check the current wi-fi connection status
        logging.debug('Check WiFi Connect')
        state = str(nmcli.device.show('wlan0')['GENERAL.STATE'].split(" ")[0])
        logging.debug(str(uuids.wifiStatus[state]))
        return uuids.wifiStatus[state]

    def ReadValue(self, options):

        logging.debug('Read WiFi Connect')
        self.WiFiStatus = self.checkWiFIStatus()
        value = []

        for c in self.WiFiStatus:
            value.append(dbus.Byte(c.encode()))
        return value


class WiFiConnectDescriptor(Descriptor):

    def __init__(self, characteristic):
        Descriptor.__init__(
                self, uuids.USER_DESC_DESCRIPTOR_UUID,
                ["read"],
                characteristic)

    def ReadValue(self, options):
        value = []
        desc = uuids.WIFI_CONNECT_KEY_VALUE

        for c in desc:
            value.append(dbus.Byte(c.encode()))
        return value


class WiFiRemoveCharacteristic(Characteristic):

    def __init__(self, service):
        self.notifying = False
        Characteristic.__init__(
                self, uuids.WIFI_REMOVE_CHARACTERISTIC_UUID,
                ["read", "write", "notify"], service)
        self.add_descriptor(WiFiRemoveDescriptor(self))
        self.add_descriptor(opaqueStructure(self))
        self.wifistatus = "False"

    def WiFiRemoveCallback(self):
        if self.notifying:
            logging.debug('Callback WiFi Remove')
            value = []
            val = self.wifistatus

            for c in val:
                value.append(dbus.Byte(c.encode()))
            self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": value}, [])

        return self.notifying

    def StartNotify(self):

        logging.debug('Notify WiFi Remove')
        if self.notifying:
            return

        self.notifying = True

        value = []

        for c in self.WiFiStatus:
            value.append(dbus.Byte(c.encode()))
        self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": value}, [])
        self.add_timeout(30000, self.WiFiRemoveCallback)

    def StopNotify(self):
        self.notifying = False

    def WriteValue(self, value, options):
        logging.debug('Write WiFi Remove')
        wifiRemoveSSID = wifi_remove_pb2.wifi_remove_v1()
        wifiRemoveSSID.ParseFromString(bytes(value))
        nmcli.connection.delete(wifiRemoveSSID.service)
        logging.debug('Connection %s should be deleted'
                      % wifiRemoveSSID.service)

    def ReadValue(self, options):
        logging.debug('Read WiFi Renove')

        value = []
        val = self.wifistatus
        for c in val:
            value.append(dbus.Byte(c.encode()))
        return value


class WiFiRemoveDescriptor(Descriptor):

    def __init__(self, characteristic):
        Descriptor.__init__(
                self, uuids.USER_DESC_DESCRIPTOR_UUID,
                ["read"],
                characteristic)

    def ReadValue(self, options):
        value = []
        desc = uuids.WIFI_REMOVE_VALUE

        for c in desc:
            value.append(dbus.Byte(c.encode()))
        return value


class EthernetOnlineCharacteristic(Characteristic):

    def __init__(self, service):
        Characteristic.__init__(
                self, uuids.ETHERNET_ONLINE_CHARACTERISTIC_UUID,
                ["read"], service)
        self.add_descriptor(EthernetOnlineDescriptor(self))
        self.add_descriptor(utf8Format(self))

    def ReadValue(self, options):

        logging.debug('Read Ethernet Online')

        value = []

        val = "false"

        if(open("/sys/class/net/eth0/carrier").readline().strip() == "1"):
            val = "true"

        for c in val:
            value.append(dbus.Byte(c.encode()))
        return value


class EthernetOnlineDescriptor(Descriptor):

    def __init__(self, characteristic):
        Descriptor.__init__(
                self, uuids.USER_DESC_DESCRIPTOR_UUID,
                ["read"],
                characteristic)

    def ReadValue(self, options):
        value = []
        desc = uuids.ETHERNET_ONLINE_VALUE

        for c in desc:
            value.append(dbus.Byte(c.encode()))
        return value


class SoftwareVersionCharacteristic(Characteristic):
    def __init__(self, service):
        Characteristic.__init__(
                self, uuids.SOFTWARE_VERSION_CHARACTERISTIC_UUID,
                ["read"], service)

    def ReadValue(self, options):
        logging.debug('Read Firmware')

        val = os.getenv('FIRMWARE_VERSION')

        value = []

        for c in val:
            value.append(dbus.Byte(c.encode()))

        return value


class utf8Format(Descriptor):

    def __init__(self, characteristic):
        Descriptor.__init__(
                self, uuids.PRESENTATION_FORMAT_DESCRIPTOR_UUID,
                ["read"],
                characteristic)

    def ReadValue(self, options):
        value = []
        value.append(dbus.Byte(0x19))
        value.append(dbus.Byte(0x00))
        value.append(dbus.Byte(0x00))
        value.append(dbus.Byte(0x00))
        value.append(dbus.Byte(0x01))
        value.append(dbus.Byte(0x00))
        value.append(dbus.Byte(0x00))

        return value


class opaqueStructure(Descriptor):

    def __init__(self, characteristic):
        Descriptor.__init__(
                self, uuids.PRESENTATION_FORMAT_DESCRIPTOR_UUID,
                ["read"],
                characteristic)

    def ReadValue(self, options):
        value = []
        value.append(dbus.Byte(0x1B))
        value.append(dbus.Byte(0x00))
        value.append(dbus.Byte(0x00))
        value.append(dbus.Byte(0x00))
        value.append(dbus.Byte(0x01))
        value.append(dbus.Byte(0x00))
        value.append(dbus.Byte(0x00))

        return value


app = Application()
app.add_service(DeviceInformationService(0))
app.add_service(HeliumService(1))
app.register()

adv = ConfigAdvertisement(0)

# Setup GPIO Devices
variant = os.getenv('VARIANT')
if (variant == "NEBHNT-IN1") or (variant == "Indoor"):
    buttonGPIO = 26
    statusGPIO = 25
else:
    buttonGPIO = 24
    statusGPIO = 25
userButton = Button(buttonGPIO, hold_time=2)
statusLed = LED(statusGPIO)


def diagnosticsThreadCode():
    logging.debug("Diagnostics Thread Started")
    global diagnosticsStatus
    while True:
        try:
            diagnosticsJsonFile = open("/var/data/nebraDiagnostics.json")
            diagnosticsJsonFile = json.load(diagnosticsJsonFile)
            if(diagnosticsJsonFile['PF'] is True):
                diagnosticsStatus = True
            else:
                diagnosticsStatus = False

        except FileNotFoundError:
            diagnosticsStatus = False

        except json.JSONDecodeError:
            diagnosticsStatus = False

        except ValueError:
            diagnosticsStatus = False
        sleep(60)


def ledThreadCode():
    logging.debug("LED Thread Started")
    global diagnosticsStatus
    global advertisementLED

    while True:
        if(diagnosticsStatus is False):
            statusLed.blink(0.1, 0.1, 10, False)
        elif(advertisementLED is True):
            statusLed.blink(1, 1, 1, False)
        else:
            statusLed.on()
            sleep(2)


advertise = True


def startAdvert():
    global advertise
    advertise = True
    logging.debug("Button press advertise queued")


def advertisementThreadCode():
    global advertise
    global advertisementLED
    global scanWifi
    logging.debug("Advertising Thread Started")
    while True:
        if(advertise is True):
            advertise = False
            scanWifi = True
            try:
                BleTools.disconnect_connections()
            except TypeError:
                # Most Likely Already Disconnected
                pass
            adv.register()
            advertisementLED = True
            sleep(300)
            adv.unregister()
            advertisementLED = False
            scanWifi = False
        else:
            sleep(5)


def wifiThreadCode():
    global scanWifi
    global wifiCache
    logging.debug("WiFi Thread Started")
    while True:
        if(scanWifi is True):
            logging.debug("Wi-Fi Scanning")
            wifiCache = nmcli.device.wifi()
            logging.debug("Wi-Fi Complete")
            sleep(15)
        else:
            sleep(5)


count = 0

appThread = threading.Thread(target=app.run)
ledThread = threading.Thread(target=ledThreadCode)
diagnosticsThread = threading.Thread(target=diagnosticsThreadCode)
advertisementThread = threading.Thread(target=advertisementThreadCode)
wifiThread = threading.Thread(target=wifiThreadCode)

userButton.when_held = startAdvert


# Main Loop Starts Here
try:
    print("Starting %s" % (count))
    # app.run()
    appThread.daemon = True
    appThread.start()
    ledThread.start()
    diagnosticsThread.start()
    wifiThread.start()
    advertisementThread.start()

except KeyboardInterrupt:
    app.quit()
    GPIO.cleanup()
except Exception as e:
    print(e)
    GPIO.cleanup()
