import textwrap

from craft_cli import BaseCommand, emit

from .. import messages
from ..storage import ClientStorage


class PingCommand(BaseCommand):
    """Pings the Landscape Server instance, if we are registered."""

    name = "ping"
    help_msg = "Pings the Landscape Server instance to which this client is registered."
    overview = textwrap.dedent(
        """
        Ping the associated Landscape Server instance.

        This client must already be registered. The response will
        indicate whether there is a pending message exchange.
    """
    )

    def fill_parser(self, parser):
        parser.add_argument(
            "--port",
            default="",
            help="Port that the Landscape Server pingserver is listening on. "
            "Default is port 80.",
        )
        parser.add_argument(
            "--timeout",
            default=None,
            help="How many seconds to wait for the server to send data before "
            "giving up",
        )

    def run(self, parsed_args):
        storage = ClientStorage()

        if not storage.get("registered"):
            emit.message("Not registered. Nothing to do.")
            return

        registration_info = storage.get("registration_info")
        server_host = registration_info["server_host"]

        port = f":{parsed_args.port}" if parsed_args.port else ""

        status_code, payload = messages.get(
            f"http://{server_host}{port}/ping",
            timeout=parsed_args.timeout,
        )

        emit.message(f"Received message: {payload}")
