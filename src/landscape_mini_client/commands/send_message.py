import argparse
import json
import textwrap

from craft_cli import BaseCommand, emit

from ..messages import MessageException, send_message
from ..storage import ClientStorage


def send_prepared_message(args: argparse.Namespace, storage: ClientStorage) -> None:
    """Sends an arbitrary message to a Landscape Server instance."""
    if "registration_info" not in storage or not storage.get("registered"):
        emit.message("Not registered - not sure where to send message")
        return

    server_host = storage["registration_info"]["server_host"]
    server_port = storage["registration_info"]["server_port"]

    with open(args.message) as message_fp:
        try:
            message = json.load(message_fp)
        except Exception as e:
            emit.message(f"There was a problem parsing '{args.message}': {e}")
            return

    message["server-uuid"] = storage["registration_info"]["server_uuid"]
    message["sequence"] = storage["next_seq"]
    secure_id = storage["registration_info"]["secure_id"]

    try:
        status_code, payload = send_message(
            f"{args.protocol}://{server_host}{server_port}/message-system",
            message,
            verify=args.verify,
            timeout=args.timeout,
            secure_id=secure_id,
        )
    except MessageException:
        emit.message("Message sending failed")
    else:
        if status_code == 200:
            emit.message("Message sent successfully")
            storage["next_seq"] = payload["next-expected-sequence"]
            storage["next_tok"] = payload["next-exchange-token"]
        else:
            emit.message("Message sending failed. Response {status_code}")

        emit.message(f"Received message: {payload}")


class SendMessageCommand(BaseCommand):
    """Sends an arbitrary message to a Landscape Server instance."""

    name = "send_message"
    help_msg = "Send an arbitrary message to a Landscape Server instance."
    overview = textwrap.dedent(
        """
        Send an arbitrary message to a Landscape Server instance.

        This will only work properly if you've already registered with the
        instance. You must provide a JSON-formatted file from which to read the
        message.
        """
    )

    def fill_parser(self, parser):
        parser.add_argument(
            "--message",
            required=True,
            help="JSON-formatted file from which to read the message."
        )
        parser.add_argument(
            "--protocol", default="https", help="Transfer protocol: http or https.",
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
        parser.add_argument(
            "--storage",
            default=".lmc-storage.pickle",
            help="File in which to store local registration and message state "
            "information",
        )

    def run(self, parsed_args):
        send_prepared_message(parsed_args, ClientStorage(parsed_args.storage))
