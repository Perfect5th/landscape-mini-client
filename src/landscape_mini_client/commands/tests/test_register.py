from argparse import Namespace
from logging import ERROR, INFO
from unittest import TestCase
from unittest.mock import ANY, patch

from ...messages import MessageException
from ..register import register


class RegisterTestCase(TestCase):

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

    def setUp(self):
        super().setUp()

        self.send_message_mock = patch(
            register.__module__ + ".send_message").start()

        self.addCleanup(patch.stopall)

    def test_register(self):
        """Happy path test."""
        self.send_message_mock.return_value = (200, "test")

        with self.assertLogs(level=INFO) as logging:
            register(self.namespace)

        self.assertEqual(len(logging.records), 2)
        self.assertIn("successful", logging.output[0])

    def test_register_suppress_warnings(self):
        """
        Tests that https warnings are filtered when args.verify is
        False.
        """
        self.send_message_mock.return_value = (200, "test")

        with patch("warnings.filterwarnings") as filterwarnings_mock:
            register(self.namespace)

        filterwarnings_mock.assert_called_once_with(
            "ignore", message="unverified https")

    def test_register_message_exception(self):
        """
        Tests that we log an error when send_message raises a
        MessageException.
        """
        self.send_message_mock.side_effect = MessageException()

        with self.assertLogs(level=ERROR) as logging:
            register(self.namespace)

        self.assertEqual(len(logging.records), 1)
        self.assertIn("failed", logging.output[0])

    def test_register_bad_status_code(self):
        """
        Tests that we log an error when send_message returns a non-200
        status_code.
        """
        self.send_message_mock.return_value = (400, None)

        with self.assertLogs(level=ERROR) as logging:
            register(self.namespace)

        self.assertEqual(len(logging.records), 1)
        self.assertIn("failed", logging.output[0])

    def test_register_specified_port(self):
        """Tests that we use the specified port if it is provided."""
        self.send_message_mock.return_value = (200, "test")

        register(Namespace(
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
        ))

        self.send_message_mock.assert_called_once_with(
            "http://localhost:8080/message-system",
            ANY,
            verify=False,
            timeout=5,
        )
