from collections import OrderedDict
from typing import Any, Dict, TextIO

import jinja2
from yaml.loader import Loader, SafeLoader
from yaml.resolver import BaseResolver

Recipe = Any


def parse_ordered_yaml(infile: str) -> Recipe:
    def ordering(loader: Loader, node: Any) -> OrderedDict:
        return OrderedDict(loader.construct_pairs(node))  # type: ignore

    loader = SafeLoader(infile)
    try:
        tag = BaseResolver.DEFAULT_MAPPING_TAG
        loader.add_constructor(tag, ordering)  # type: ignore
        return loader.get_single_data()
    finally:
        loader.dispose()  # type: ignore


def parse_recipe(infile: TextIO, config: Dict[str, Any]) -> Recipe:
    source = infile.read()
    template = jinja2.Template(source)
    rendered_source = template.render(**config)
    recipe = parse_ordered_yaml(rendered_source)
    return recipe
