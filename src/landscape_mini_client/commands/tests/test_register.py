from argparse import Namespace
from http.server import HTTPServer, HTTPStatus, BaseHTTPRequestHandler
from threading import Thread
from typing import Callable
from unittest import TestCase

import requests

from ..register import register


class MockHTTPRequestHandler(BaseHTTPRequestHandler):
    get_callback = lambda self: ""

    def do_HEAD(self):
        self.send_response(HTTPStatus.OK)

    def do_GET(self):
        response = self.get_callback().encode()

        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Content-Length", len(response))
        self.end_headers()

        self.wfile.write(response)

    def do_POST(self):
        self.do_GET()


def start_test_server(**kwargs) -> HTTPServer:
    if "get_callback" in kwargs:
        MockHTTPRequestHandler.get_callback = kwargs["get_callback"]

    server = HTTPServer(('localhost', 8081), MockHTTPRequestHandler)

    thread = Thread(target=server.serve_forever)
    thread.start()

    return server


class RegisterTestCase(TestCase):

    def test_register(self):
        server = start_test_server(get_callback=lambda self: "Hello, world!")
        self.addCleanup(server.shutdown)

        register(Namespace(
            account_name="test",
            computer_title="test",
            server_host=server.server_address[0],
            port=server.server_port,
            verify=False,
            registration_key="",
            tags="",
            container_info="",
            vm_info="",
            protocol="http",
        ))
