import logging
from time import sleep


RETRY_SLEEP_SECONDS = 60

"""
Loads the onboarding file and returns 

pub_key, onboarding_key, animal_name
"""

def read_onboarding_key(onboarding_key_filepath):
    while True:
        try:
            public_keys_file = open(onboarding_key_filepath).readline().split('"')
            break
        except FileNotFoundError:
            logging.debug('Waiting for keyfile in %s. Will try again in %s seconds' % (onboarding_key_filepath, RETRY_SLEEP_SECONDS))
            sleep(RETRY_SLEEP_SECONDS)

    # Keyfile exists, now running.
    pub_key = str(public_keys_file[1])
    onboarding_key = str(public_keys_file[3])
    animal_name = str(public_keys_file[5])

    return pub_key, onboarding_key, animal_name

def read_eth0_mac_address(eth0_mac_address_filepath):
    return open(eth0_mac_address_filepath) \
            .readline() \
            .strip() \
            .upper()