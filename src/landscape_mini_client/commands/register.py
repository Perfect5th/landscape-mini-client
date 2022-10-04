import argparse
import logging
import socket
import time
import warnings

import requests

from ..util import bpickle


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

    pickled = bpickle.dumps(message)

    try:
        response = requests.post(
            f"{args.protocol}://{args.server_host}:{args.port}/message-system",
            data=pickled.encode(),
            verify=args.verify,
            headers={
                "User-Agent": "landscape-mini-client/0.0.1",
                "X-Message-Api": "3.3",
                "Content-Type": "application/octet-stream",
            },
        )
    except requests.exceptions.ConnectTimeout:
        logging.error(f"Connection to {args.server_host} timed out")
    else:
        if response.status_code == 200:
            logging.info("Registration request successful")
            logging.debug(f"Response 200: {response.content}")
        else:
            logging.error(f"Registration failed. Response "
                          f"{response.status_code}: {response.content}")

        payload, _ = bpickle.loads(response.content)

        logging.info(f"Received message: {payload}")
