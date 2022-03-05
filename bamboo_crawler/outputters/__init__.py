import hashlib
import json
import sys
from typing import Any, Dict, Optional, Union

import boto3
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.sql import text

from .. import interface


class StdoutOutputter(interface.Outputter):
    def write(
        self, value: Union[str, bytes], *, context: Optional[interface.Context] = None
    ) -> None:
        if isinstance(value, bytes):
            value = value.decode()
        sys.stdout.write(value)


class SQSS3Outputter(interface.Outputter):
    def __init__(
        self,
        bucket_name: str,
        queue_name: str,
        *,
        s3_config: Dict[str, Any] = {},
        sqs_config: Dict[str, Any] = {},
    ) -> None:
        super().__init__()
        s3 = boto3.resource("s3", **s3_config)
        sqs = boto3.resource("sqs", **sqs_config)
        bucket = s3.Bucket(bucket_name)
        queue = sqs.get_queue_by_name(QueueName=queue_name)
        self.bucket = bucket
        self.queue = queue

    def write(
        self,
        value: Union[str, bytes],
        *,
        context: Optional[interface.Context] = None,
    ) -> None:
        bucket = self.bucket
        queue = self.queue
        encoding = sys.getdefaultencoding()
        if context is not None:
            metadata = context.metadata
        else:
            metadata = {}
        if isinstance(value, str):
            value = value.encode(encoding)

        name = hashlib.sha256(value).hexdigest()
        obj = bucket.Object(name)
        obj.put(
            Body=value,
            ContentEncoding=encoding,
            ContentType="text/plain",
        )
        j = json.dumps({"s3_body": obj.key, "metadata": metadata})
        queue.send_message(MessageBody=j)


class SQLOutputter(interface.Outputter):
    def __init__(
        self, url: str, *, table: Optional[str] = None, query: Optional[str] = None
    ) -> None:
        self.query: Union[sqlalchemy.sql.Insert, str]
        if query is None and table is None:
            raise NotImplementedError
        if query is not None and table is not None:
            raise NotImplementedError
        self.engine = sqlalchemy.create_engine(url)
        self._type = "query"
        if table is not None:
            self._type = "table"
            metadata = sqlalchemy.MetaData()
            metadata.reflect(self.engine, only=[table])
            Base = automap_base(metadata=metadata)
            Base.prepare()
            self.query = metadata.tables[table].insert()
        else:
            assert query is not None
            self.query = query

    def write(
        self,
        value: Union[str, bytes],
        *,
        context: Optional[interface.Context] = None,
    ) -> None:
        j = json.loads(value)
        if self._type == "table":
            assert isinstance(self.query, sqlalchemy.sql.Insert)
            self.engine.execute(self.query.values(j))
        else:
            assert isinstance(self.query, str)
            self.engine.execute(text(self.query), j)


__all__ = ["StdoutOutputter", "SQSS3Outputter", "SQLOutputter"]
