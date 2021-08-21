import os

from gatewayconfig.logger import logger
from gatewayconfig.gatewayconfig_app import GatewayconfigApp

VARIANT = os.getenv('VARIANT')
SENTRY_DSN = os.getenv('SENTRY_DSN') # https://docs.sentry.io/product/sentry-basics/dsn-explainer/
BALENA_DEVICE_UUID = os.getenv('BALENA_DEVICE_UUID')
BALENA_APP_NAME = os.getenv('BALENA_APP_NAME')
FIRMWARE_VERSION = os.getenv('FIRMWARE_VERSION')
ETH0_MAC_ADDRESS_PATH = os.getenv('ETH0_MAC_ADDRESS_PATH', '/sys/class/net/eth0/address')
WIFI_MAC_ADDRESS_PATH = os.getenv('WIFI_MAC_ADDRESS_PATH', '/sys/class/net/wlan0/address')
MINER_KEYS_FILEPATH = os.getenv('MINER_KEYS_FILEPATH', '/var/data/public_keys')
DIAGNOSTICS_JSON_FILEPATH = os.getenv('DIAGNOSTICS_JSON_FILEPATH', '/var/data/nebraDiagnostics.json')
ETHERNET_IS_ONLINE_FILEPATH = os.getenv('ETHERNET_IS_ONLINE_FILEPATH', '/sys/class/net/eth0/carrier')

def main():
    validate_env()
    start()

def validate_env():
    logger.debug("Starting with the following ENV:\n\
        SENTRY_DSN=%s\n\
        BALENA_APP_NAME=%s\n\
        BALENA_DEVICE_UUID=%s\n\
        VARIANT=%s\n\
        ETH0_MAC_ADDRESS_PATH=%s\n\
        WIFI_MAC_ADDRESS_PATH=%s\n\
        MINER_KEYS_FILEPATH=%s\n\
        DIAGNOSTICS_JSON_FILEPATH=%s\n\
        ETHERNET_IS_ONLINE_FILEPATH=%s\n\
        FIRMWARE_VERSION=%s\n" % 
        (SENTRY_DSN, BALENA_APP_NAME, BALENA_DEVICE_UUID, VARIANT, ETH0_MAC_ADDRESS_PATH, 
            WIFI_MAC_ADDRESS_PATH, MINER_KEYS_FILEPATH, DIAGNOSTICS_JSON_FILEPATH, 
            ETHERNET_IS_ONLINE_FILEPATH, FIRMWARE_VERSION))

def start():
    config_app = GatewayconfigApp(SENTRY_DSN, BALENA_APP_NAME, BALENA_DEVICE_UUID, VARIANT, 
        ETH0_MAC_ADDRESS_PATH, MINER_KEYS_FILEPATH, DIAGNOSTICS_JSON_FILEPATH, ETHERNET_IS_ONLINE_FILEPATH, FIRMWARE_VERSION)

    try:
        config_app.start()
    except Exception as e:
        logger.error(e)
        config_app.stop()

if __name__ == "__main__":
    main()