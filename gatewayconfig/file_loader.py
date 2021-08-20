import json
from retry import retry
from gatewayconfig.logger import logger
from gatewayconfig.constants import ETHERNET_IS_ONLINE_CARRIER_VAL
RETRY_SLEEP_SECONDS = 60

"""
Loads the onboarding file and returns 

pub_key, onboarding_key, animal_name
"""

@retry(FileNotFoundError, delay=RETRY_SLEEP_SECONDS, logger=logger)

# Onboarding key originally created in helium/miner: https://github.com/helium/miner/blob/bdfbbe9db5809598b210f564d3d206eee56dfdf7/src/miner_keys.erl
# Then copied as part of hm-miner: https://github.com/NebraLtd/hm-miner/blob/2fdfa76de1a398c0a876075aced1e0332ca211f1/start-miner.sh
def read_miner_keys(miner_keys_filepath):

    with open(miner_keys_filepath) as miner_keys_file:
        miner_keys = {}

        for line in miner_keys_file.readlines():
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
                    miner_keys[key] = json_line[key]
            except json.JSONDecodeError:
                miner_keys[key] = False

    # Keyfile exists, now running.
    pub_key = miner_keys['pubkey']
    onboarding_key = miner_keys['onboarding_key']
    animal_name = miner_keys['animal_name']

    return pub_key, onboarding_key, animal_name

def read_eth0_mac_address(eth0_mac_address_filepath):
    return open(eth0_mac_address_filepath) \
            .readline() \
            .strip() \
            .upper()

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