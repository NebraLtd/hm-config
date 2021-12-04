from unittest import TestCase
from unittest.mock import MagicMock

# Test Cases
from subprocess import CalledProcessError  # nosec
from gatewayconfig.nmcli_custom import CustomSystemCommand, enable_use_sudo
from gatewayconfig.nmcli_custom import _syscmd
from gatewayconfig.nmcli_custom import disable_use_sudo

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


class Error(Exception):
    # Mock exception object
    stderr = 'error_message'.encode('utf-8')
    returncode = 255


class TestCustomSystemCommandHandleError(TestCase):
    sys_command = None

    def setUp(self):
        self.sys_command = CustomSystemCommand()

    def tearDown(self):
        del self.sys_command

    def _test_handle_returncode(self, rc, expected, err=None):
        if not err:
            err = Error()
            err.returncode = rc

        exception = False
        exception_type = None

        try:
            self.sys_command._handle_error(err)
        except Exception as e:
            exception = True
            exception_type = e

        self.assertTrue(exception)
        self.assertIsInstance(exception_type, expected)

    def test_handle_rc_2(self):
        # Expect return code 2 to raise InvalidUserInputException.
        self._test_handle_returncode(2, InvalidUserInputException)

    def test_handle_rc_3(self):
        # Expect return code 3 to raise TimeoutExpiredException.
        self._test_handle_returncode(3, TimeoutExpiredException)

    def test_handle_rc_4(self):
        # Expect return code 4 to raise ConnectionActivateFailedException.
        self._test_handle_returncode(4, ConnectionActivateFailedException)

    def test_handle_rc_5(self):
        # Expect return code 5 to raise ConnectionDeactivateFailedException.
        self._test_handle_returncode(5, ConnectionDeactivateFailedException)

    def test_handle_rc_6(self):
        # Expect return code 6 to raise DisconnectDeviceFailedException.
        self._test_handle_returncode(6, DisconnectDeviceFailedException)

    def test_handle_rc_7(self):
        # Expect return code 7 to raise ConnectionDeleteFailedException.
        self._test_handle_returncode(7, ConnectionDeleteFailedException)

    def test_handle_rc_8(self):
        # Expect return code 8 to raise NetworkManagerNotRunningException.
        self._test_handle_returncode(8, NetworkManagerNotRunningException)

    def test_handle_rc_10(self):
        # Expect return code 10 to raise NetworkManagerNotRunningException.
        self._test_handle_returncode(10, NotExistException)

    def test_handle_rc_1_scanning_not_allowed(self):
        # Expect return code 1 to raise ScanningNotAllowedException when
        # stderr contains "Scanning not allowed"
        err = Error()
        err.returncode = 1
        err.stderr = 'Some output Scanning not allowed :-)'.encode('utf-8')
        self._test_handle_returncode(
            1,
            ScanningNotAllowedException,
            err=err
        )

    def test_handle_rc_other(self):
        # If there is an unknown return code raise an UnspecifiedException.
        self._test_handle_returncode(255, UnspecifiedException)


class TestDisableUseSudo(TestCase):

    def test_use_sudo_disabled_default(self):
        self.assertFalse(_syscmd._use_sudo)

    def test_use_sudo(self):
        # Check that calling disable_use_sudo actually toggles the
        # use_sudo flag within the CustomSystemCommand object.
        enable_use_sudo()
        self.assertTrue(_syscmd._use_sudo)
        disable_use_sudo()
        self.assertFalse(_syscmd._use_sudo)


class MockNMCLIResponse():
    stdout = 'stdout text'.encode('utf-8')


def raise_called_process_error_exception(*args, **kwargs):
    raise CalledProcessError(5, 'Error')


class TestCustomSystemCommandNMCLI(TestCase):
    sys_command = None

    def setUp(self):
        self.sys_command = CustomSystemCommand()
        self.sys_command._run = MagicMock()

    def tearDown(self):
        del self.sys_command

    def test_disable_sudo(self):
        self.sys_command._run.return_value = MockNMCLIResponse()
        self.sys_command.disable_use_sudo()
        result = self.sys_command.nmcli(['params', 'here'])
        self.assertEqual(result, 'stdout text')
        self.assertTrue(self.sys_command._run.called)
        self.sys_command._run.assert_called_with(
            ['nmcli', 'params', 'here'],
            capture_output=True,
            check=True
        )

    def test_list_params(self):
        self.sys_command._run.return_value = MockNMCLIResponse()
        result = self.sys_command.nmcli(['params', 'here'])
        self.assertEqual(result, 'stdout text')
        self.assertTrue(self.sys_command._run.called)
        self.sys_command._run.assert_called_with(
            ['sudo', 'nmcli', 'params', 'here'],
            capture_output=True,
            check=True
        )

    def test_string_params(self):
        self.sys_command._run.return_value = MockNMCLIResponse()
        result = self.sys_command.nmcli('params here')
        self.assertEqual(result, 'stdout text')
        self.assertTrue(self.sys_command._run.called)
        self.sys_command._run.assert_called_with(
            ['sudo', 'nmcli', 'params here'],
            capture_output=True,
            check=True
        )

    def test_handle_called_process_error_exception(self):
        self.sys_command._run.side_effect = \
            raise_called_process_error_exception
        self.sys_command._handle_error = MagicMock()
        result = self.sys_command.nmcli('params here')

        # We shouldn't get a result as we expect an exception to be
        # thrown and the handle_error method to be called.
        self.assertEqual(result, None)
        self.sys_command._handle_error.assert_called()
