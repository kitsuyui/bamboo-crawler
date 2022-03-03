import functools
import json
import pathlib
import sys
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple, Union

import boto3
import sqlalchemy
from sqlalchemy.ext.automap import automap_base

from .. import interface


@dataclass
class ConstantInputter(interface.Inputter):
    value: Union[str, bytes]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def read(self) -> interface.Context:
        return interface.Context(self.value, **self.metadata)


class StdinInputter(interface.Inputter):
    def read(self) -> interface.Context:
        return interface.Context(sys.stdin.read())


class FileInputter(interface.Inputter):
    def __init__(self, filepath: str) -> None:
        self.path = pathlib.Path(filepath).resolve()

    def read(self) -> interface.Context:
        return interface.Context(self.path.open().read())


SQSQueue = Any
S3Bucket = Any
SQSMessage = Any


@dataclass
class SQSS3Inputter(interface.Inputter):
    bucket_name: str
    queue_name: str
    s3_config: Dict[str, Any] = field(default_factory=dict)
    sqs_config: Dict[str, Any] = field(default_factory=dict)
    message: Optional[SQSMessage] = None

    @functools.cached_property
    def queue(self) -> SQSQueue:
        sqs = boto3.resource("sqs", **self.sqs_config)
        queue = sqs.get_queue_by_name(QueueName=self.queue_name)
        return queue

    @functools.cached_property
    def bucket(self) -> S3Bucket:
        s3 = boto3.resource("s3", **self.s3_config)
        return s3.Bucket(self.bucket_name)

    def read(self) -> interface.Context:
        message = self.__read_sqs()
        body, meta = self.__read_s3(message)
        return interface.Context(body, **meta)

    def __read_sqs(self) -> SQSMessage:
        if self.message is not None:
            return self.message

        messages = list(self.queue.receive_messages())
        while not messages:
            time.sleep(5)
            messages = list(self.queue.receive_messages())

        message = messages[0]
        self.message = message
        return message

    def __read_s3(self, message: SQSMessage) -> Tuple[str, Dict[str, Any]]:
        j = json.loads(message.body)
        obj = self.bucket.Object(j["s3_body"])
        metadata = j["metadata"]
        response = obj.get()
        return response["Body"].read(), metadata

    def done(self) -> None:
        super().done()
        if self.message is not None:
            self.message.delete()
            self.message = None


class SQLInputter(interface.Inputter):
    def __init__(
        self, url: str, *, table: Optional[str] = None, query: Optional[str] = None
    ) -> None:
        if query is None and table is None:
            raise NotImplementedError
        if query is not None and table is not None:
            raise NotImplementedError
        self.engine = sqlalchemy.create_engine(url)
        if table is not None:
            metadata = sqlalchemy.MetaData()
            metadata.reflect(self.engine, only=[table])
            Base = automap_base(metadata=metadata)
            Base.prepare()
            select_query = metadata.tables[table].select()
        else:
            select_query = None

        if select_query is not None:
            self.result = self.engine.execute(select_query)
        else:
            self.result = self.engine.execute(query)
        self.keys = list(self.result.keys())

    def read(self) -> interface.Context:
        r = self.result.fetchone()
        if r is None:
            return interface.Context(None)
        p = dict(zip(self.keys, list(r)))
        return interface.Context(p)


__all__ = [
    "ConstantInputter",
    "StdinInputter",
    "FileInputter",
    "SQSS3Inputter",
    "SQLInputter",
]
