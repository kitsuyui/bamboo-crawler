import time
from dataclasses import dataclass
from typing import Optional

from .interface import Deserializer, Inputter, Outputter, Processor, Serializer


@dataclass
class Task:
    name: str
    inputter: Inputter
    processor: Processor
    outputter: Outputter
    deserializer: Optional[Deserializer] = None
    serializer: Optional[Serializer] = None

    def do(self) -> None:
        context = self.inputter.read()
        body = context.body
        if self.deserializer is not None:
            body = self.deserializer.deserialize(body)
        for d in self.processor.process(body, context=context):
            job_name = self.name
            class_name = self.processor.__class__.__name__
            metadatakey = "processed_time_{}_{}".format(job_name, class_name)
            timestamp = int(time.time())
            context.add_metadata(**{metadatakey: timestamp})
            if self.serializer is not None:
                d = self.serializer.serialize(d)
            self.outputter.write(d, context=context)
        self.inputter.done()
