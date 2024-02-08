"""Simple pickler based on landscape.lib.bpickle."""

from typing import List, Mapping, Tuple, Union


def dumps(payload: Union[dict, list, str, int]) -> bytes:
    if isinstance(payload, dict):
        return _dumps_dict(payload)

    if isinstance(payload, list):
        return _dumps_list(payload)

    if isinstance(payload, str):
        return f"u{len(payload)}:{payload}".encode()

    if isinstance(payload, bytes):
        return f"b{len(payload)}:".encode() + payload

    if isinstance(payload, int):
        return f"i{payload};".encode()


def _dumps_dict(payload: Mapping[str, Union[dict, list, str, int]]) -> bytes:
    pickled = [b"d"]

    for k, v in payload.items():
        pickled.append(f"u{len(k)}:{k}".encode())
        pickled.append(dumps(v))

    pickled.append(b";")
    pickled = b"".join(pickled)

    return pickled


def _dumps_list(payload: List[Union[dict, list, str, int]]) -> bytes:
    pickled = [b"l"]

    for v in payload:
        pickled.append(dumps(v))

    pickled.append(b";")
    pickled = b"".join(pickled)

    return pickled


def loads(payload: bytes) -> Tuple[Union[dict, list, str, int], int]:
    typecode = chr(payload[0])

    if typecode == "d":
        return loads_dict(payload)

    if typecode == "l":
        return loads_list(payload)

    if typecode == "u":
        length, rest = payload[1:].split(b":", maxsplit=1)
        length = int(length)
        string = rest[:length].decode()
        return string, length + len(f"u{length}:")

    if typecode == "s":
        length, rest = payload[1:].split(b":", maxsplit=1)
        length = int(length)
        bytestring = rest[:length]
        return bytestring, length + len(f"s{length}:")

    if typecode == "b":
        length = payload.find(b";", 1)
        number = int(payload[1:length])
        return bool(number), len(f"b{number}")

    if typecode == "i":
        length = payload.find(b";", 1)
        number = int(payload[1:length])
        return number, len(f"i{number};")


def loads_dict(payload: bytes) -> Tuple[dict, int]:
    index = 1
    result = {}

    while chr(payload[index]) != ";":
        key, inc = loads(payload[index:])
        index += inc
        value, inc = loads(payload[index:])
        index += inc

        result[key] = value

    return result, index + 1


def loads_list(payload: bytes) -> Tuple[list, int]:
    index = 1
    result = []

    while chr(payload[index]) != ";":
        value, inc = loads(payload[index:])
        index += inc

        result.append(value)

    return result, index + 1
