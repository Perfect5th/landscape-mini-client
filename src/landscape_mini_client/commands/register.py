import argparse
import logging
import socket
import time
import warnings

from ..messages import MessageException, send_message


def register(args: argparse.Namespace) -> None:
    """Registers this client with a Landscape Server instance."""

    if not args.verify:
        warnings.filterwarnings("ignore", message="unverified https")

    message = {
        "messages": [{
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
        }]
    }

    try:
        status_code, payload = send_message(
            f"{args.protocol}://{args.server_host}:{args.port}/message-system",
            message,
            verify=args.verify,
            timeout=args.timeout,
        )
    except MessageException:
        logging.error("Registration failed.")
    else:
        if status_code == 200:
            logging.info("Registration request successful")
        else:
            logging.error(f"Registration failed. Response {status_code}")

        logging.info(f"Received message: {payload}")
