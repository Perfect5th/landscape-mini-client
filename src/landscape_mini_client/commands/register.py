import argparse
import socket
import textwrap
import time
import warnings

from craft_cli import BaseCommand, emit

from ..messages import MessageException, send_message
from ..storage import ClientStorage


def register(args: argparse.Namespace, storage: ClientStorage) -> None:
    """Registers this client with a Landscape Server instance."""
    if storage.get("registered"):
        emit.message("Already registered. Nothing to do.")
        return

    if not args.verify:
        warnings.filterwarnings("ignore", message="unverified https")

    message = {
        "messages": [
            {
                "type": "register",
                "hostname": socket.gethostname(),
                "account_name": args.account_name,
                "computer_title": args.computer_title,
                "registration_password": args.registration_key,
                "tags": args.tags,
                "container-info": args.container_info,
                "vm-info": args.vm_info,
                "timestamp": int(time.time()),
                "api": "3.3",
            }
        ]
    }

    port = f":{args.port}" if args.port else ""

    try:
        status_code, payload = send_message(
            f"{args.protocol}://{args.server_host}{port}/message-system",
            message,
            verify=args.verify,
            timeout=args.timeout,
        )
    except MessageException:
        emit.message("Registration failed")
    else:
        if status_code == 200:
            emit.message("Registration request successful")
            storage["registered"] = True
        else:
            emit.message(f"Registration failed. Response {status_code}")

        emit.message(f"Received message: {payload}")


class RegisterCommand(BaseCommand):
    """Registers this client with a Landscape Server instance."""

    name = "register"
    help_msg = "Register with a Landscape Server instance."
    overview = textwrap.dedent(
        """
        Register with a Landscape Server instance.

        An account name and computer title must be provided, as well as
        the domain name or IP address of the Landscape Server instance.

        A registration request message will be sent to the server.
    """
    )

    def fill_parser(self, parser):
        parser.add_argument(
            "--account-name",
            required=True,
            help="Name of your account in Landscape Server.",
        )
        parser.add_argument(
            "--computer-title",
            required=True,
            help="Identifier for this computer in Landscape.",
        )
        parser.add_argument(
            "--server-host",
            required=True,
            help="Domain name or IP address of Landscape Server.",
        )
        parser.add_argument(
            "--registration-key", default="", help="Landscape registration key."
        )
        parser.add_argument(
            "--tags", default="", help="Tags to add to this machine's Landscape record."
        )
        parser.add_argument(
            "--container-info",
            default="",
            help="Identifier for what type of container this machine is "
            "containerized with.",
        )
        parser.add_argument(
            "--vm-info",
            default="",
            help="Identifier for what type of virtual machine this machine is "
            "virtualized with.",
        )
        parser.add_argument(
            "--protocol", default="https", help="Transfer protocol: http or https."
        )
        parser.add_argument(
            "--port",
            default="",
            help="Port that the Landscape Server instance is listening on. "
            "Default is based on protocol.",
        )
        parser.add_argument(
            "--no-verify",
            action="store_false",
            dest="verify",
            help="Do not verify SSL/TLS",
        )
        parser.add_argument(
            "--timeout",
            default=None,
            help="How many seconds to wait for the server to send data before "
            "giving up",
        )

    def run(self, parsed_args):
        register(parsed_args, ClientStorage())
