import os
import pickle
from typing import Any, Mapping

from collections.abc import MutableMapping


class ClientStorage(MutableMapping):
    """A pickle-file-backed dictionary."""

    def __init__(self, loc: str = ".lmc-storage.pickle"):
        super().__init__()

        if not os.path.exists(loc):
            with open(loc, "wb") as loc_fp:
                pickle.dump({}, loc_fp)

        self._loc = loc

    def get(self, key):
        try:
            return self[key]
        except KeyError:
            return None

    def _read_loc(self):
        with open(self._loc, "rb") as loc_fp:
            return pickle.load(loc_fp)

    def _write_loc(self, payload):
        with open(self._loc, "wb") as loc_fp:
            pickle.dump(payload, loc_fp)

    def __delitem__(self, key):
        stored = self._read_loc()

        if key not in stored:
            return

        del stored[key]
        self._write_loc(stored)

    def __getitem__(self, key):
        stored = self._read_loc()

        return stored[key]

    def __iter__(self):
        return iter(self._read_loc())

    def __len__(self):
        return len(self._read_loc())

    def __setitem__(self, key, value):
        stored = self._read_loc()

        stored[key] = value
        self._write_loc(stored)

    def clear(self):
        with open(self._loc, "wb") as loc_fp:
            pickle.dump({}, loc_fp)


def put(item_dict: Mapping[str, Any], loc: str = ".lmc-storage.pickle") -> None:
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
