from unittest import TestCase
from unittest.mock import patch, mock_open

from gatewayconfig.file_loader import read_eth0_mac_address, read_wlan0_mac_address, read_ethernet_is_online


class TestFileLoader(TestCase):

    @patch(
            "builtins.open",
            new_callable=mock_open,
            read_data='a1:B2:c3:Dd:e5:f7'
    )
    def test_read_eth0_mac_address(self, eth0_file_mock):
        eth0_mac = read_eth0_mac_address('val/not/used')

        self.assertEqual(eth0_mac, 'A1:B2:C3:DD:E5:F7')

    @patch(
            "builtins.open",
            new_callable=mock_open,
            read_data='a1:B2:c3:Dd:e5:f7'
    )
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
