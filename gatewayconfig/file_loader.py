from gatewayconfig.logger import get_logger
from gatewayconfig.constants import ETHERNET_IS_ONLINE_CARRIER_VAL

logger = get_logger(__name__)
RETRY_SLEEP_SECONDS = 60


def read_eth0_mac_address(eth0_mac_address_filepath):
    try:
        return open(eth0_mac_address_filepath) \
                .readline() \
                .strip() \
                .upper()
    except FileNotFoundError:
        return "FF:FF:FF:FF:FF:FF"


def read_wlan0_mac_address(wlan0_mac_address_filepath):
    try:
        return open(wlan0_mac_address_filepath) \
                .readline() \
                .strip() \
                .upper()
    except FileNotFoundError:
        return "FF:FF:FF:FF:FF:FF"


def read_ethernet_is_online(ethernet_is_online_filepath):
    is_ethernet_online = "false"

    ethernet_is_online_carrier_val = open(ethernet_is_online_filepath).readline().strip()
    if(ethernet_is_online_carrier_val == ETHERNET_IS_ONLINE_CARRIER_VAL):
        is_ethernet_online = "true"

    return is_ethernet_online
