import argparse
import socket
import time
from typing import List, Mapping, Union

import requests


def pickle_dict(payload: Mapping[str, Union[dict, list, str, int]]) -> str:
    pickled = ["d"]

    for k, v in payload.items():
        pickled.append(f"u{len(k)}:{k}")
        pickled.append(pickle(v))

    pickled.append(";")
    pickled = "".join(pickled)

    return pickled


def pickle_list(payload: List[Union[dict, list, str, int]]) -> str:
    pickled = ["l"]

    for v in payload:
        pickled.append(pickle(v))

    pickled.append(";")
    pickled = "".join(pickled)

    return pickled


def pickle(payload: Union[dict, list, str, int]) -> str:
    """Simple pickler based on landscape.lib.bpickle."""

    if isinstance(payload, dict):
        return pickle_dict(payload)

    if isinstance(payload, list):
        return pickle_list(payload)

    if isinstance(payload, str):
        return f"u{len(payload)}:{payload}"

    if isinstance(payload, int):
        return f"i{payload};"


def register(args: argparse.Namespace) -> None:
    """Registers this client with a Landscape Server instance."""

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

    pickled = pickle(message)
    breakpoint()

    response = requests.post(
        "https://10.76.244.123/message-system",
        data=pickled.encode(),
        verify=False,
        headers={
            "User-Agent": "landscape-client/18.01-0ubuntu13",
            "X-Message-Api": "3.3",
            "Content-Type": "application/octet-stream",
        },
    )

    print(response)
