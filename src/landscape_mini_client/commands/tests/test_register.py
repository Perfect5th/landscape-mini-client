from argparse import Namespace
from unittest.mock import ANY, patch

import pytest

from ...messages import MessageException
from ..register import register


@pytest.fixture
def send_message_mock():
    send_message_patch = patch(f"{register.__module__}.send_message")
    yield send_message_patch.start()
    send_message_patch.stop()


@pytest.fixture
def storage():
    return {}


class TestRegister:
    namespace = Namespace(
        account_name="test",
        computer_title="test",
        registration_key="",
        tags="",
        container_info="",
        vm_info="",
        protocol="http",
        server_host="localhost",
        port="",
        timeout=5,
        verify=False,
    )

    def test_register(self, emitter, send_message_mock, storage):
        """Happy path test."""
        send_message_mock.return_value = (200, "test")

        register(self.namespace, storage)

        emitter.assert_message("Registration request successful")

    def test_register_suppress_warnings(self, send_message_mock, storage):
        """
        Tests that https warnings are filtered when args.verify is
        False.
        """
        send_message_mock.return_value = (200, "test")

        with patch("warnings.filterwarnings") as filterwarnings_mock:
            register(self.namespace, storage)

        filterwarnings_mock.assert_called_once_with(
            "ignore", message="unverified https"
        )

    def test_register_message_exception(self, emitter, send_message_mock, storage):
        """
        Tests that we log an error when send_message raises a
        MessageException.
        """
        send_message_mock.side_effect = MessageException()

        register(self.namespace, storage)

        emitter.assert_message("Registration failed")

    def test_register_bad_status_code(self, emitter, send_message_mock, storage):
        """
        Tests that we log an error when send_message returns a non-200
        status_code.
        """
        send_message_mock.return_value = (400, None)

        register(self.namespace, storage)

        emitter.assert_message("Registration failed. Response 400")

    def test_register_specified_port(self, send_message_mock, storage):
        """Tests that we use the specified port if it is provided."""
        send_message_mock.return_value = (200, "test")

        register(
            Namespace(
                verify=False,
                account_name="test",
                computer_title="test",
                registration_key="test",
                tags="test",
                container_info="test",
                vm_info="test",
                port="8080",
                protocol="http",
                server_host="localhost",
                timeout=5,
            ),
            storage,
        )

        send_message_mock.assert_called_once_with(
            "http://localhost:8080/message-system",
            ANY,
            verify=False,
            timeout=5,
        )
