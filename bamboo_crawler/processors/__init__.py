import functools
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime, time
from typing import Any, Dict, Iterable, List, Optional, Union
from urllib.parse import parse_qs, urlparse

import lxml.html
import requests

from .. import interface


@dataclass
class HTTPCrawler(interface.Crawler):
    headers: Dict = field(default_factory=dict)

    def crawl(
        self, url: Union[str, bytes], *, context: Optional[interface.Context] = None
    ) -> Iterable[Union[str, bytes]]:
        resp = requests.get(url, headers=self.headers)
        yield resp.content


@dataclass
class XPathScraper(interface.Scraper):
    xpaths: Dict[str, str]

    def scrape(
        self, data: Union[str, bytes], *, context: Optional[interface.Context] = None
    ) -> Iterable[Dict[str, Any]]:
        elements = lxml.html.fromstring(data)
        j = {key: elements.xpath(xpath) for key, xpath in self.xpaths.items()}
        yield j


@dataclass
class SingleXPathScraper(interface.Scraper):
    xpath: str

    def scrape(
        self, data: Union[str, bytes], *, context: Optional[interface.Context] = None
    ) -> Iterable[Union[str, bytes]]:
        element = lxml.html.fromstring(data)
        elements = element.xpath(self.xpath)
        k = [str(x) for x in elements]  # type: ignore
        yield from k


@dataclass
class CSSSelectorScraper(interface.Scraper):
    selectors: Dict[str, str]

    def scrape(
        self, data: Union[str, bytes], *, context: Optional[interface.Context] = None
    ) -> Iterable[Dict[str, Any]]:
        elements = lxml.html.fromstring(data)
        j = {
            key: self.__select(elements, p_selector)
            for key, p_selector in self.selectors.items()
        }
        yield j

    def __select(self, elements: Any, p_selector: Union[str, bytes]) -> List[str]:
        if isinstance(p_selector, (str, bytes)):
            return [e.text_content() for e in elements.cssselect(p_selector)]
        selector, attribute = p_selector
        return [e.attrib[attribute] for e in elements.cssselect(selector)]


@dataclass
class MixedHTMLScraper(interface.Scraper):
    targets: Dict[str, Dict[str, str]] = field(default_factory=dict)

    @functools.cached_property
    def xpath_scraper(self) -> XPathScraper:
        xpaths = {
            key: target["xpath"]
            for key, target in self.targets.items()
            if "xpath" in target
        }
        return XPathScraper(xpaths=xpaths)

    @functools.cached_property
    def cssselector_scraper(self) -> CSSSelectorScraper:
        css = {
            key: target["css"]
            for key, target in self.targets.items()
            if "css" in target
        }
        return CSSSelectorScraper(selectors=css)

    def scrape(
        self, data: Union[str, bytes], *, context: Optional[interface.Context] = None
    ) -> Iterable[Dict[str, Any]]:
        d1 = list(self.xpath_scraper.scrape(data))[0]
        d2 = list(self.cssselector_scraper.scrape(data))[0]
        yield self.__merge(d1, d2)

    def __merge(self, *scraped_data_list: Dict[str, Any]) -> Dict[str, Any]:
        d = defaultdict(list)
        for data in scraped_data_list:
            for key, values in data.items():
                d[key].extend(values)
        return dict(d)


class NullProcessor(interface.Processor):
    def process(
        self, data: Union[str, bytes], *, context: Optional[interface.Context] = None
    ) -> Iterable[Union[str, bytes]]:
        yield data


@dataclass
class PythonProcessor(interface.Processor):
    mappers: Dict[str, str]

    def __safe_eval(self, code: str, data: Any, metadata: Dict[str, Any]) -> Any:
        def extract_digit(data: str) -> str:
            return "".join(x for x in data if x.isdigit())

        allowed_functions = {
            "int": int,
            "float": float,
            "str": str,
            "extract_digit": extract_digit,
            "urlparse": urlparse,
            "parse_qs": parse_qs,
            "date": date,
            "time": time,
            "datetime": datetime,
            "max": max,
            "all": all,
            "any": any,
            "divmod": divmod,
            "sorted": sorted,
            "ord": ord,
            "chr": chr,
            "bin": bin,
            "sum": sum,
            "pow": pow,
            "len": len,
            "range": range,
            "map": map,
            "re": re,
        }
        globals_ = {"__builtins__": allowed_functions}
        locals_ = {"_": data, "meta": metadata}
        try:
            return eval(code, globals_, locals_)
        except Exception:
            return None

    def process(
        self, data: Union[str, bytes], *, context: Optional[interface.Context] = None
    ) -> Iterable[Dict[str, Any]]:
        yield {
            key: self.__safe_eval(
                code, data, metadata=context.metadata if context else {}
            )
            for key, code in self.mappers.items()
        }


__all__ = [
    "HTTPCrawler",
    "XPathScraper",
    "SingleXPathScraper",
    "CSSSelectorScraper",
    "NullProcessor",
]
