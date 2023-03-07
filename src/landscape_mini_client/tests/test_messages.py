from http.server import HTTPServer, HTTPStatus, BaseHTTPRequestHandler
from logging import ERROR
from time import sleep
from threading import Thread
from unittest import TestCase

from ..messages import MessageException, send_message
from ..util import bpickle


class MockHTTPRequestHandler(BaseHTTPRequestHandler):
    def get_callback(self):
        return bpickle.dumps("test")

    def post_callback(self):
        return bpickle.dumps("test")

    def do_HEAD(self):
        self.send_response(HTTPStatus.OK)

    def do_GET(self):
        self._respond(self.get_callback())

    def do_POST(self):
        self._respond(self.post_callback())

    def _respond(self, response):
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Content-Length", len(response))
        self.end_headers()

        self.wfile.write(response)


def start_test_server(**kwargs) -> HTTPServer:
    for method in ("head", "get", "post"):
        callback = f"{method}_callback"
        if callback in kwargs:
            setattr(MockHTTPRequestHandler, callback, kwargs[callback])

    port = kwargs.get("port", 8081)
    server = HTTPServer(("localhost", port), MockHTTPRequestHandler)

    thread = Thread(target=server.serve_forever)
    thread.start()

    return server


class SendMessageTestCase(TestCase):
    def test_send_message_success(self):
        """
        Tests that we return the status code and payload after a message
        is successfully sent.
        """
        server = start_test_server()
        self.addCleanup(server.shutdown)

        if hasattr(self, "assertNoLogs"):
            # py3.10
            with self.assertNoLogs(level=ERROR):
                status_code, payload = send_message(
                    f"http://{server.server_address[0]}:{server.server_port}",
                    message={"test": "message"},
                    verify=False,
                )
        else:
            # py3.8
            status_code, payload = send_message(
                f"http://{server.server_address[0]}:{server.server_port}",
                message={"test": "message"},
                verify=False,
            )

        self.assertEqual(status_code, 200)
        self.assertEqual(payload, "test")

    def test_send_message_timeout(self):
        """
        Tests that we log an error and raise a MessageException if the
        connection or read times out.
        """

        def sleep_timeout(_):
            sleep(1)
            return b""

        server = start_test_server(
            post_callback=sleep_timeout,
            port=8082,
        )
        self.addCleanup(server.shutdown)

        with self.assertLogs(level=ERROR) as logging:
            self.assertRaises(
                MessageException,
                send_message,
                f"http://{server.server_address[0]}:{server.server_port}",
                message={"test": "message"},
                verify=False,
                timeout=0.2,
            )

        self.assertEqual(len(logging.records), 1)

    def test_send_message_connection_error(self):
        """
        Tests that we log an error and raise a MessageException if the
        connection fails.
        """
        with self.assertLogs(level=ERROR) as logging:
            self.assertRaises(
                MessageException,
                send_message,
                "http://localhost:8083",
                message={"test": "message"},
                verify=False,
            )

        self.assertEqual(len(logging.records), 1)

    def test_send_message_ssl_error(self):
        """
        Tests that we log an error and raise a MessageException if SSL
        validation or handshake fails.
        """
        server = start_test_server(port=8084)
        self.addCleanup(server.shutdown)

        with self.assertLogs(level=ERROR) as logging:
            self.assertRaises(
                MessageException,
                send_message,
                f"https://{server.server_address[0]}:{server.server_port}",
                message={"test": "message"},
                verify=True,
            )

        self.assertEqual(len(logging.records), 1)
