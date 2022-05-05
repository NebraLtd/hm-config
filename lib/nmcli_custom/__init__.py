from nmcli import GeneralControl
from nmcli import NetworkingControl
from nmcli import RadioControl
from nmcli import DeviceControl
from nmcli import ConnectionControl
from ._system_custom import CustomSystemCommand

_syscmd = CustomSystemCommand()
connection = ConnectionControl(_syscmd)
device = DeviceControl(_syscmd)
general = GeneralControl(_syscmd)
networking = NetworkingControl(_syscmd)
radio = RadioControl(_syscmd)


def disable_use_sudo():
    _syscmd.disable_use_sudo()


def enable_use_sudo():
    _syscmd._use_sudo = True


disable_use_sudo()
