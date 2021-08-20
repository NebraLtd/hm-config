from unittest import TestCase
from unittest.mock import patch, mock_open

from gatewayconfig.file_loader import read_eth0_mac_address, read_wlan0_mac_address, read_ethernet_is_online, read_miner_keys

class TestFileLoader(TestCase):

    MINER_KEYS_FILE_MOCK = '{}\n{}\n{}'.format(
        '{pubkey, "112mPWkGW55kcbQTgbtJvgAKMSTrEhHgavrdF1Cbu8FU85tTL4Nc"}.',
        '{onboarding_key, "112mPWkGW55kcbQTgbtJvgAKMSTrEhHgavrdF1Cbu8FU85tTL142"}.',
        '{animal_name, "gigantic-basil-turtle"}.'
    )

    @patch("builtins.open", new_callable=mock_open, read_data=MINER_KEYS_FILE_MOCK)
    def test_read_miner_keys(self, miner_keys_file_mock):
        pub_key, onboarding_key, animal_name = read_miner_keys('val/not/used')

        self.assertEqual(pub_key, '112mPWkGW55kcbQTgbtJvgAKMSTrEhHgavrdF1Cbu8FU85tTL4Nc')
        self.assertEqual(onboarding_key, '112mPWkGW55kcbQTgbtJvgAKMSTrEhHgavrdF1Cbu8FU85tTL142')
        self.assertEqual(animal_name, 'gigantic-basil-turtle')

    @patch("builtins.open", new_callable=mock_open, read_data='a1:B2:c3:Dd:e5:f7')
    def test_read_eth0_mac_address(self, eth0_file_mock):
        eth0_mac = read_eth0_mac_address('val/not/used')

        self.assertEqual(eth0_mac, 'A1:B2:C3:DD:E5:F7')

    @patch("builtins.open", new_callable=mock_open, read_data='a1:B2:c3:Dd:e5:f7')
    def test_read_wlan0_mac_address(self, wlan0_file_mock):
        eth0_mac = read_wlan0_mac_address('val/not/used')

        self.assertEqual(eth0_mac, 'A1:B2:C3:DD:E5:F7')

    # Defaults to FF if file not found
    def test_read_wlan0_mac_address_default(self):
        eth0_mac = read_wlan0_mac_address('file/not/mocked')

        self.assertEqual(eth0_mac, 'FF:FF:FF:FF:FF:FF')

    @patch("builtins.open", new_callable=mock_open, read_data='1')
    def test_read_ethernet_is_online(self, eth0_file_mock):
        ethernet_is_online = read_ethernet_is_online('val/not/used')

        self.assertEqual(ethernet_is_online, 'true')

    @patch("builtins.open", new_callable=mock_open, read_data='0')
    def test_read_ethernet_is_offline(self, eth0_file_mock):
        ethernet_is_online = read_ethernet_is_online('val/not/used')

        self.assertEqual(ethernet_is_online, 'false')