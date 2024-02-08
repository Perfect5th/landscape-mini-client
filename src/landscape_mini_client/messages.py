import logging
import warnings
from typing import Optional, Tuple

import requests
from requests.exceptions import ConnectionError, ConnectTimeout, ReadTimeout, SSLError

from .util import bpickle


API_HEADERS = {
    "User-Agent": "landscape-mini-client/0.0.1",
    "X-Message-Api": "3.3",
    "Content-Type": "application/octet-stream",
}
COMPUTER_ID_HEADER = "X-Computer-ID"


class MessageException(Exception):
    """Exception type for failed message attempts."""

    pass


def send_message(
    url: str,
    message: dict,
    secure_id: Optional[str] = None,
    **kwargs,
) -> Tuple[int, dict]:
    """
    A thin-ish wrapper around requests that adds some error logging.
    """
    if not kwargs.get("verify"):
        warnings.filterwarnings("ignore", message="unverified https")

    pickled = bpickle.dumps(message)
    headers = API_HEADERS.copy()

    if secure_id:
        headers[COMPUTER_ID_HEADER] = secure_id

    try:
        response = requests.post(
            url,
            data=pickled,
            **kwargs,
            headers=headers,
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


def get(url: str, **kwargs):
    try:
        response = requests.post(
            url,
            **kwargs,
            headers=API_HEADERS,
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
