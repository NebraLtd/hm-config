import os

from gatewayconfig.logger import logger
from gatewayconfig.gatewayconfig_app import GatewayconfigApp

VARIANT = os.getenv('VARIANT')
SENTRY_DSN = os.getenv('SENTRY_DSN') # https://docs.sentry.io/product/sentry-basics/dsn-explainer/
BALENA_DEVICE_UUID = os.getenv('BALENA_DEVICE_UUID')
BALENA_APP_NAME = os.getenv('BALENA_APP_NAME')
FIRMWARE_VERSION = os.getenv('FIRMWARE_VERSION')
ETH0_MAC_ADDRESS_FILEPATH = os.getenv('ETH0_MAC_ADDRESS_FILEPATH', '/sys/class/net/eth0/address')
WLAN0_MAC_ADDRESS_FILEPATH = os.getenv('WLAN0_MAC_ADDRESS_FILEPATH', '/sys/class/net/wlan0/address')
MINER_KEYS_FILEPATH = os.getenv('MINER_KEYS_FILEPATH', '/var/data/public_keys')
DIAGNOSTICS_JSON_URL = os.getenv('DIAGNOSTICS_JSON_URL', 'http://localhost:80?json=true')
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
        ETH0_MAC_ADDRESS_FILEPATH=%s\n\
        WLAN0_MAC_ADDRESS_FILEPATH=%s\n\
        MINER_KEYS_FILEPATH=%s\n\
        DIAGNOSTICS_JSON_URL=%s\n\
        ETHERNET_IS_ONLINE_FILEPATH=%s\n\
        FIRMWARE_VERSION=%s\n" % 
        (SENTRY_DSN, BALENA_APP_NAME, BALENA_DEVICE_UUID, VARIANT, ETH0_MAC_ADDRESS_FILEPATH, 
            WLAN0_MAC_ADDRESS_FILEPATH, MINER_KEYS_FILEPATH, DIAGNOSTICS_JSON_URL, 
            ETHERNET_IS_ONLINE_FILEPATH, FIRMWARE_VERSION))

def start():
    config_app = GatewayconfigApp(SENTRY_DSN, BALENA_APP_NAME, BALENA_DEVICE_UUID, VARIANT, 
        ETH0_MAC_ADDRESS_FILEPATH, WLAN0_MAC_ADDRESS_FILEPATH, MINER_KEYS_FILEPATH, DIAGNOSTICS_JSON_URL, ETHERNET_IS_ONLINE_FILEPATH, FIRMWARE_VERSION)

    try:
        config_app.start()
    except Exception:
        logger.exception('__main__ failed for unknown reason')
        config_app.stop()

if __name__ == "__main__":
    main()