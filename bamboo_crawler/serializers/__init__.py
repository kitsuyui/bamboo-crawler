import json
from typing import Union

from .. import interface


class NullSerializer(interface.Serializer):
    def serialize(self, value: Union[str, bytes]) -> Union[str, bytes]:
        return value


class JSONSerializer(interface.Serializer):
    def serialize(self, value: Union[str, bytes]) -> Union[str, bytes]:
        return json.dumps(value)


__all__ = ["NullSerializer", "JSONSerializer"]
