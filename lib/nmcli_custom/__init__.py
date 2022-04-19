from subprocess import CalledProcessError  # nosec
from typing import List, Union

from nmcli import GeneralControl
from nmcli import NetworkingControl
from nmcli import RadioControl
from nmcli import SystemCommand
from nmcli import DeviceControl
from nmcli import ConnectionControl

from nmcli._exception import (
    ConnectionActivateFailedException,
    ConnectionDeactivateFailedException,
    ConnectionDeleteFailedException,
    DisconnectDeviceFailedException,
    InvalidUserInputException,
    NetworkManagerNotRunningException,
    NotExistException,
    ScanningNotAllowedException,
    TimeoutExpiredException,
    UnspecifiedException
)

CommandParameter = Union[str, List[str]]


class CustomSystemCommand(SystemCommand):

    @staticmethod
    def _handle_error(e):
        rc = e.returncode
        stderr = e.stderr.decode('utf-8')
        if rc == 2:
            raise InvalidUserInputException(
                'Invalid user input, wrong nmcli invocation') from e
        elif rc == 3:
            raise TimeoutExpiredException('Timeout expired') from e
        elif rc == 4:
            raise ConnectionActivateFailedException(
                'Connection activation failed') from e
        elif rc == 5:
            raise ConnectionDeactivateFailedException(
                'Connection deactivation failed') from e
        elif rc == 6:
            raise DisconnectDeviceFailedException(
                'Disconnecting device failed') from e
        elif rc == 7:
            raise ConnectionDeleteFailedException(
                'Connection deletion failed') from e
        elif rc == 8:
            raise NetworkManagerNotRunningException(
                'NetworkManager is not running') from e
        elif rc == 10:
            raise NotExistException(
                'Connection, device, or access point does not exist') \
                from e
        else:
            if rc == 1 and stderr.find('Scanning not allowed') > 0:
                raise ScanningNotAllowedException(stderr) from e
            raise UnspecifiedException(
                'Unknown or unspecified error [code:%d, detail:%s]'
                % (rc, stderr)
            ) from e

    def nmcli(self, parameters: CommandParameter) -> str:
        if isinstance(parameters, str):
            parameters = [parameters]
        c = ['sudo', 'nmcli'] if self._use_sudo else ['nmcli']
        commands = c + parameters
        try:
            r = self._run(commands, capture_output=True, check=True)
            return r.stdout.decode('utf-8')
        except CalledProcessError as e:
            self._handle_error(e)


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
