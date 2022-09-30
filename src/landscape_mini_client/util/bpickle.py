"""Simple pickler based on landscape.lib.bpickle."""

from typing import List, Mapping, Union


def dumps(payload: Union[dict, list, str, int]) -> str:
    if isinstance(payload, dict):
        return _dumps_dict(payload)

    if isinstance(payload, list):
        return _dumps_list(payload)

    if isinstance(payload, str):
        return f"u{len(payload)}:{payload}"

    if isinstance(payload, int):
        return f"i{payload};"


def _dumps_dict(payload: Mapping[str, Union[dict, list, str, int]]) -> str:
    pickled = ["d"]

    for k, v in payload.items():
        pickled.append(f"u{len(k)}:{k}")
        pickled.append(dumps(v))

    pickled.append(";")
    pickled = "".join(pickled)

    return pickled


def _dumps_list(payload: List[Union[dict, list, str, int]]) -> str:
    pickled = ["l"]

    for v in payload:
        pickled.append(dumps(v))

    pickled.append(";")
    pickled = "".join(pickled)

    return pickled
