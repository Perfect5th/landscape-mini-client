import random
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
        parser.add_argument(
            "--storage",
            default=".lmc-storage.pickle",
            help="File in which to store local registration and message state "
            "information",
        )
        parser.add_argument(
            "--randomize-id",
            action="store_true",
            dest="randomize_id",
            help="If provided, the insecure ID sent to the server will be "
            "random",
        )
        parser.add_argument(
            "--increment-id",
            action="store_true",
            dest="increment_id",
            help="If provided, the insecure ID is incremented each time it is "
            "sent. Overrides 'randomize-id'",
        )

    def run(self, parsed_args):
        storage = ClientStorage(loc=parsed_args.storage)

        if not storage.get("registered"):
            emit.message("Not registered. Nothing to do.")
            return

        registration_info = storage.get("registration_info")
        server_host = registration_info["server_host"]

        if parsed_args.increment_id:
            last_id = storage.get("last_id")
            if last_id is None:
                last_id = 0
            insecure_id = last_id + 1
            storage["last_id"] = last_id + 1
        elif parsed_args.randomize_id:
            insecure_id = random.randint(1, 100_000)
        else:
            insecure_id = registration_info["insecure_id"]

        port = f":{parsed_args.port}" if parsed_args.port else ""

        status_code, payload = messages.get(
            f"http://{server_host}{port}/ping?insecure_id={insecure_id}",
            timeout=parsed_args.timeout,
        )

        emit.message(f"Received message: {payload}")
