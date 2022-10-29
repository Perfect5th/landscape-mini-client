import os
import pickle
from typing import Mapping


def put(
        item_dict: Mapping[str, any],
        loc: str = ".lmc-storage.pickle"
) -> None:
    """Stores an item in persistent storage."""
    if not os.path.exists(loc):
        with open(loc, "wb") as loc_fp:
            pickle.dump(item_dict, loc_fp)
    else:
        with open(loc, "rb") as loc_fp:
            try:
                stored = pickle.load(loc_fp)
            except EOFError:
                stored = {}

        stored.update(item_dict)

        with open(loc, "wb") as loc_fp:
            pickle.dump(stored, loc_fp)


def get(item_key, loc: str = ".lmc-storage.pickle") -> any:
    """Fetches an item from persistent storage."""
    if not os.path.exists(loc):
        return None

    with open(loc, "rb") as loc_fp:
        try:
            stored = pickle.load(loc_fp)
        except EOFError:
            return None

    return stored.get(item_key)
