#!/usr/bin/python3
import os
import sentry_sdk
import dbus
import logging
import sys
import json
import nmcli
import h3
import threading
import uuids

# From imports
from time import sleep
from RPi import GPIO
from variant_definitions import variant_definitions

# BLE Library
from advertisement import Advertisement
from service import Application
from service import Service
from service import Characteristic
from service import Descriptor
from bletools import BleTools

# Protobuf Imports
import add_gateway_pb2
import assert_location_pb2
import diagnostics_pb2
import wifi_connect_pb2
import wifi_remove_pb2
import wifi_services_pb2

from gpiozero import Button, LED

# ET Phone Home
VARIANT = os.getenv('VARIANT')
SENTRY_KEY = os.getenv('SENTRY_CONFIG')
BALENA_ID = os.getenv('BALENA_DEVICE_UUID')
BALENA_APP = os.getenv('BALENA_APP_NAME')
uuids.FIRMWARE_VERSION = os.getenv('FIRMWARE_VERSION')
sentry_sdk.init(SENTRY_KEY, environment=BALENA_APP)
sentry_sdk.set_user({"id": BALENA_ID})
sentry_sdk.set_context("variant", {VARIANT})

VARIANT_DETAILS = variant_definitions[VARIANT]

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
PUBLIC_KEY = str(public_keys_file[1])
ONBOARDING_KEY = str(public_keys_file[3])
# The animal name isn't used anywhere, why do we even declare it?
# ANIMAL_NAME = str(public_keys_file[5])


# Setup Thread Variables
advertisement_led = False
diagnostics_status = False
scan_wifi = False
wifi_cache = []

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)


class ConfigAdvertisement(Advertisement):
    # BLE advertisement
    def __init__(self, index):
        global VARIANT_DETAILS
        Advertisement.__init__(self, index, "peripheral")
        variant = VARIANT_DETAILS['APPNAME']
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
        val = ONBOARDING_KEY

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
        val = PUBLIC_KEY
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

    global wifi_cache

    def __init__(self, service):
        Characteristic.__init__(
                self, uuids.WIFI_SERVICES_CHARACTERISTIC_UUID,
                ["read"], service)
        self.add_descriptor(WiFiServicesDescriptor(self))
        self.add_descriptor(OpaqueStructure(self))

    def ReadValue(self, options):
        logging.debug('Read WiFi Services')
        wifi_ssids = wifi_services_pb2.wifi_services_v1()

        for network in wifi_cache:
            ssid = str(network.ssid)
            if(ssid != "--" and ssid != ""):
                if(ssid not in wifi_ssids.services):
                    wifi_ssids.services.append(ssid)
                    logging.debug(ssid)
        value = []
        val = wifi_ssids.SerializeToString()

        for c in val:
            value.append(dbus.Byte(c))
        if("offset" in options):
            reduced_list = value[int(options["offset"]):]
            return reduced_list
        else:
            return value


class WiFiServicesDescriptor(Descriptor):

    def __init__(self, characteristic):
        Descriptor.__init__(
            self, uuids.USER_DESC_DESCRIPTOR_UUID,
            ["read"],
            characteristic
        )

    def ReadValue(self, options):
        value = []
        desc = uuids.WIFI_SERVICES_VALUE

        for c in desc:
            value.append(dbus.Byte(c.encode()))
        return value


class WiFiConfiguredServicesCharacteristic(Characteristic):

    global wifi_cache

    def __init__(self, service):
        Characteristic.__init__(
                self, uuids.WIFI_CONFIGURED_SERVICES_CHARACTERISTIC_UUID,
                ["read"], service)
        self.add_descriptor(WiFiConfiguredServicesDescriptor(self))
        self.add_descriptor(OpaqueStructure(self))

    def ReadValue(self, options):
        logging.debug('Read WiFi CONFIGURED Services')
        wifi_configured = wifi_services_pb2.wifi_services_v1()

        for network in wifi_cache:
            if(network.ssid != "--"):
                if(network.in_use):
                    active_connection = str(network.ssid)
                    wifi_configured.services.append(active_connection)
                    logging.info('Active WiFi Connection: %s'
                                 % active_connection)
        value = []
        val = wifi_configured.SerializeToString()

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
        self.add_descriptor(OpaqueStructure(self))
        self.p2pstatus = ""

    def ReadValue(self, options):  # noqa: C901
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
            eth_ip = nmcli.device.show('eth0')['IP4.ADDRESS[1]'][:-3]
        except KeyError:
            pass
        try:
            wlan_ip = nmcli.device.show('wlan0')['IP4.ADDRESS[1]'][:-3]
        except KeyError:
            pass

        ip_address = "0.0.0.0"  # nosec
        if('ethIP' in locals()):
            ip_address = str(eth_ip)
        elif('wlanIP' in locals()):
            ip_address = str(wlan_ip)

        diagnostics_proto = diagnostics_pb2.diagnostics_v1()
        diagnostics_proto.diagnostics['connected'] = str(self.p2pstatus[0][1])
        diagnostics_proto.diagnostics['dialable'] = str(self.p2pstatus[1][1])
        diagnostics_proto.diagnostics['height'] = str(self.p2pstatus[3][1])
        diagnostics_proto.diagnostics['nat_type'] = str(self.p2pstatus[2][1])
        try:
            diagnostics_proto.diagnostics['eth'] = \
                open("/sys/class/net/eth0/address").readline(). \
                strip().replace(":", "")
        except FileNotFoundError:
            diagnostics_proto.diagnostics['eth'] = "FF:FF:FF:FF:FF:FF"
        diagnostics_proto.diagnostics['fw'] = os.getenv('FIRMWARE_VERSION')
        diagnostics_proto.diagnostics['ip'] = ip_address
        try:
            wifi_diag = open("/sys/class/net/wlan0/address").readline(). \
                strip().replace(":", "")
            diagnostics_proto.diagnostics['wifi'] = wifi_diag
        except FileNotFoundError:
            diagnostics_proto.diagnostics['wifi'] = "FF:FF:FF:FF:FF:FF"
        logging.debug('items added to proto')
        value = []
        val = diagnostics_proto.SerializeToString()
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

    global wifi_cache

    def __init__(self, service):
        Characteristic.__init__(
                self, uuids.WIFI_SSID_CHARACTERISTIC_UUID,
                ["read"], service)
        self.add_descriptor(WiFiSSIDDescriptor(self))
        self.add_descriptor(utf8Format(self))

    def ReadValue(self, options):

        logging.debug('Read WiFi SSID')
        active_connection = ""
        for network in wifi_cache:
            if(network.ssid != "--"):
                if(network.in_use):
                    active_connection = str(network.ssid)
                    logging.info('Active Connection: %s' % active_connection)
        value = []

        for c in active_connection:
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
        self.add_descriptor(OpaqueStructure(self))
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
        miner_assertion_request = \
            miner_interface. \
            AssertLocation(h3String,
                           assLocDet.owner, assLocDet.nonce, assLocDet.amount,
                           assLocDet.fee, assLocDet.payer)
        # logging.debug(assLocDet)
        self.notifyValue = miner_assertion_request

    def ReadValue(self, options):
        logging.debug('Read Assert Location')
        # logging.debug(options)
        if("offset" in options):
            reduced_list = self.notifyValue[int(options["offset"]):]
            return reduced_list
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
        self.add_descriptor(OpaqueStructure(self))
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
        add_gw_details = add_gateway_pb2.add_gateway_v1()
        # logging.debug('PB2C')
        add_gw_details.ParseFromString(bytes(value))
        # logging.debug('PB2P')
        # logging.debug(str(addGatewayDetails))
        miner_bus = dbus.SystemBus()
        miner_object = miner_bus.get_object('com.helium.Miner', '/')
        sleep(0.05)
        miner_interface = dbus.Interface(miner_object, 'com.helium.Miner')
        sleep(0.05)
        add_miner_request = \
            miner_interface. \
            AddGateway(add_gw_details.owner, add_gw_details.fee,
                       add_gw_details.amount, add_gw_details.payer)
        # logging.debug(addMinerRequest)
        logging.debug("Adding Response")
        self.notifyValue = add_miner_request

    def ReadValue(self, options):
        logging.debug('Read Add Gateway')
        if("offset" in options):
            reduced_list = self.notifyValue[int(options["offset"]):]
            return reduced_list
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
        self.add_descriptor(OpaqueStructure(self))
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
        wifi_details = wifi_connect_pb2.wifi_connect_v1()
        # logging.debug('PB2C')
        wifi_details.ParseFromString(bytes(value))
        # logging.debug('PB2P')
        self.WiFiStatus = "already"
        logging.debug(str(wifi_details.service))

        nmcli.device.wifi_connect(str(wifi_details.service),
                                  str(wifi_details.password))
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
        self.add_descriptor(OpaqueStructure(self))
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
        wifi_remove_ssid = wifi_remove_pb2.wifi_remove_v1()
        wifi_remove_ssid.ParseFromString(bytes(value))
        nmcli.connection.delete(wifi_remove_ssid.service)
        logging.debug('Connection %s should be deleted'
                      % wifi_remove_ssid.service)

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


class OpaqueStructure(Descriptor):

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
    button_gpio = 26
    status_gpio = 25
else:
    button_gpio = 24
    status_gpio = 25
user_button = Button(button_gpio, hold_time=2)
status_led = LED(status_gpio)


def diagnosticsThreadCode():
    logging.debug("Diagnostics Thread Started")
    global diagnostics_status
    while True:
        try:
            diagnosticsJsonFile = open("/var/data/nebraDiagnostics.json")
            diagnosticsJsonFile = json.load(diagnosticsJsonFile)
            if(diagnosticsJsonFile['PF'] is True):
                diagnostics_status = True
            else:
                diagnostics_status = False

        except FileNotFoundError:
            diagnostics_status = False

        except json.JSONDecodeError:
            diagnostics_status = False

        except ValueError:
            diagnostics_status = False
        sleep(60)


def ledThreadCode():
    logging.debug("LED Thread Started")
    global diagnostics_status
    global advertisement_led

    while True:
        if(diagnostics_status is False):
            status_led.blink(0.1, 0.1, 10, False)
        elif(advertisement_led is True):
            status_led.blink(1, 1, 1, False)
        else:
            status_led.on()
            sleep(2)


advertise = True


def startAdvert():
    global advertise
    advertise = True
    logging.debug("Button press advertise queued")


def advertisementThreadCode():
    global advertise
    global advertisement_led
    global scan_wifi
    logging.debug("Advertising Thread Started")
    while True:
        if(advertise is True):
            advertise = False
            scan_wifi = True
            try:
                BleTools.disconnect_connections()
            except TypeError:
                # Most Likely Already Disconnected
                pass
            adv.register()
            advertisement_led = True
            sleep(300)
            adv.unregister()
            advertisement_led = False
            scan_wifi = False
        else:
            sleep(5)


def wifiThreadCode():
    global scan_wifi
    global wifi_cache
    logging.debug("WiFi Thread Started")
    while True:
        if(scan_wifi is True):
            logging.debug("Wi-Fi Scanning")
            wifi_cache = nmcli.device.wifi()
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

user_button.when_held = startAdvert


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
