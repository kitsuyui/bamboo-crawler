import gzip
import json
from typing import Any, Union

from .. import interface


class GzipDeserializer(interface.Deserializer):
    def deserialize(self, value: Union[str, bytes]) -> Any:
        if isinstance(value, str):
            value = value.encode()
        return gzip.decompress(value)


class JSONDeserializer(interface.Deserializer):
    def deserialize(self, value: Union[str, bytes]) -> Any:
        if isinstance(value, bytes):
            value = value.decode("utf-8")
        return json.loads(value)


class NullDeserializer(interface.Deserializer):
    def deserialize(self, value: Union[str, bytes]) -> Any:
        return value


__all__ = ["GzipDeserializer", "NullDeserializer", "JSONDeserializer"]
