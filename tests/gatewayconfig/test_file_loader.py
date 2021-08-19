from unittest import TestCase
from unittest.mock import patch, mock_open

from gatewayconfig.file_loader import read_eth0_mac_address, read_onboarding_key

class TestFileLoader(TestCase):

    @patch("builtins.open", new_callable=mock_open, read_data='other0"onboarding_key1"other2"pub_key3"other4"animal_name5')
    def test_read_onboarding_key(self, onboarding_file_mock):
        onboarding_key, pub_key, animal_name = read_onboarding_key('val/not/used')

        self.assertEqual(onboarding_key, 'onboarding_key1')
        self.assertEqual(pub_key, 'pub_key3')
        self.assertEqual(animal_name, 'animal_name5')

    @patch("builtins.open", new_callable=mock_open, read_data='a1:B2:c3:Dd:e5:f7')
    def test_read_eth0_mac_address(self, eth0_file_mock):
        eth0_mac = read_eth0_mac_address('val/not/used')

        self.assertEqual(eth0_mac, 'A1:B2:C3:DD:E5:F7')