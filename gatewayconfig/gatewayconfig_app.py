#!/usr/bin/python3

import os
import sentry_sdk
import logging
import sys
import json
import nmcli_custom
import h3

import threading
# From imports
from time import sleep
from RPi import GPIO
import gatewayconfig.constants as constants
from variant_definitions import variant_definitions

# BLE Library
from service import Application
from bletools import BleTools

from gpiozero import Button, LED

# ET Phone Home
variant = os.getenv('VARIANT')
sentry_key = os.getenv('SENTRY_CONFIG')
balena_id = os.getenv('BALENA_DEVICE_UUID')
balena_app = os.getenv('BALENA_APP_NAME')
constants.FIRMWARE_VERSION = os.getenv('FIRMWARE_VERSION')
sentry_sdk.init(sentry_key, environment=balena_app)
sentry_sdk.set_user({"id": balena_id})
sentry_sdk.set_context("variant", {variant})

variantDetails = variant_definitions[variant]

# Disable sudo for nmcli
nmcli_custom.disable_use_sudo()


GATT_CHRC_IFACE = "org.bluez.GattCharacteristic1"
NOTIFY_TIMEOUT = 5000

# Public Onboarding Keys
while True:
    if os.path.isfile('/var/data/public_keys'):
        public_keys = {}
        with open("/var/data/public_keys") as f:
            for line in f.readlines():
                # This is insanely ugly, but it gets the
                # job done until we switch to the API
                erlang_to_json = line.replace('.', '').\
                    replace(',', ': ').\
                    replace('pubkey', '"pubkey"').\
                    replace('onboarding_key', '"onboarding_key"').\
                    replace('animal_name', '"animal_name"')

                # Let's future proof this just
                # in case something changes later
                try:
                    json_line = json.loads(erlang_to_json)
                    for key in json_line.keys():
                        public_keys[key] = json_line[key]
                except json.JSONDecodeError:
                    pass

        pubKey = public_keys.get('pubkey', False)
        onboardingKey = public_keys.get('onboarding_key', False)
        animalName = public_keys.get('animal_name', False)
    else:
        print('File public key file not found. Going to sleep')
        sleep(60)

# Setup Thread Variables
advertisementLED = False
diagnosticsStatus = False
scanWifi = False
wifiCache = []

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

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
            wifiCache = nmcli_custom.device.wifi()
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
