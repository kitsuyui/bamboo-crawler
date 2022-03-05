from __future__ import annotations

from typing import Any, Iterable, Optional, Protocol, Union


class Inputter(Protocol):
    def read(self) -> Context:
        ...

    def done(self) -> None:
        ...


class Outputter(Protocol):
    def write(
        self, value: Union[str, bytes], *, context: Optional[Context] = None
    ) -> None:
        ...


class Processor(Protocol):
    def process(
        self, value: Union[str, bytes], *, context: Optional[Context] = None
    ) -> Iterable[Any]:
        ...


class Crawler(Processor):
    def process(
        self, value: Union[str, bytes], *, context: Optional[Context] = None
    ) -> Iterable[Any]:
        yield from self.crawl(value, context=context)

    def crawl(
        self, location: Union[str, bytes], *, context: Optional[Context] = None
    ) -> Iterable[Any]:
        ...


class Scraper(Processor):
    def process(
        self, value: Union[str, bytes], *, context: Optional[Context] = None
    ) -> Iterable[Any]:
        yield from self.scrape(value, context=context)

    def scrape(
        self, data: Union[str, bytes], *, context: Optional[Context] = None
    ) -> Iterable[Any]:
        ...


class Deserializer(Protocol):
    def deserialize(self, data: Union[str, bytes]) -> Any:
        ...


class Serializer(Protocol):
    def serialize(self, value: Any) -> Union[str, bytes]:
        ...


class Context(object):
    def __init__(self, body: Any, **kwargs: Any) -> None:
        self.body = body
        self.metadata = kwargs.copy()

    def add_metadata(self, **kwargs: Any) -> None:
        self.metadata.update(kwargs)
