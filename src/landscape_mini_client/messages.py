import logging
import warnings

import requests
from requests.exceptions import ConnectionError, ConnectTimeout, ReadTimeout, SSLError

from .util import bpickle


class MessageException(Exception):
    """Exception type for failed message attempts."""

    pass


def send_message(
    url: str,
    message: dict,
    **kwargs,
) -> (int, dict):
    """
    A thin-ish wrapper around requests that adds some error logging.
    """
    if not kwargs.get("verify"):
        warnings.filterwarnings("ignore", message="unverified https")

    pickled = bpickle.dumps(message)

    try:
        response = requests.post(
            url,
            data=pickled,
            **kwargs,
            headers={
                "User-Agent": "landscape-mini-client/0.0.1",
                "X-Message-Api": "3.3",
                "Content-Type": "application/octet-stream",
            },
        )
    except (ConnectTimeout, ReadTimeout):
        logging.error(f"Connection to {url} timed out")

        raise MessageException()
    except ConnectionError:
        logging.error(f"Connection to {url} failed")
        raise MessageException()
    except SSLError as e:
        logging.error(e.strerror)
        raise MessageException()
    else:
        payload, _ = bpickle.loads(response.content)

        return response.status_code, payload
