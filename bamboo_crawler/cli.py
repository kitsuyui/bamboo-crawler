import argparse
import logging
import sys
import time
from typing import Any, Dict, List, TextIO

import yaml

from . import deserializers, inputters, outputters, processors, serializers
from .parser import parse_recipe
from .task import Task


def _set_logger(debug: bool = False) -> logging.Logger:
    logger = logging.getLogger(__name__)
    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.ERROR)
    fmt = logging.Formatter(logging.BASIC_FORMAT)
    ch = logging.StreamHandler(sys.stderr)
    ch.setFormatter(fmt)
    logger.addHandler(ch)
    return logger


def pickup_class(directive: Dict[str, Any], search_classes: Any) -> Any:
    return getattr(search_classes, directive["type"])


def subtask_from_directive(directive: Dict[str, Any], search_classes: Any) -> Any:
    options = directive.get("options", {})
    class_ = pickup_class(directive, search_classes)
    target = class_(**options)
    return target


def task_from_definition(
    name: str, inputters: Any, outputters: Any, processors: Any, definitions: Any
) -> Task:
    d = definitions
    reserved_keywords = frozenset(
        {"input", "output", "process", "deserialize", "serialize"}
    )
    if frozenset(d.keys()) > reserved_keywords:
        raise NotImplementedError

    inputter = subtask_from_directive(d["input"], inputters)
    outputter = subtask_from_directive(d["output"], outputters)
    processor = subtask_from_directive(d["process"], processors)

    if "deserialize" in d:
        deserializer = subtask_from_directive(d["deserialize"], deserializers)
    else:
        deserializer = None

    if "serialize" in d:
        serializer = subtask_from_directive(d["serialize"], serializers)
    else:
        serializer = None

    task = Task(
        name=name,
        inputter=inputter,
        processor=processor,
        outputter=outputter,
        deserializer=deserializer,
        serializer=serializer,
    )
    return task


def job_(recipe: Dict[str, Any], tasks: List[str], duration: float) -> None:
    logger = logging.getLogger(__name__)
    for key in tasks:
        definitions = recipe[key]
        task = task_from_definition(
            key,
            inputters,
            outputters,
            processors,
            definitions,
        )
        logger.debug("begin: " + key)
        task.do()
        logger.debug("end: " + key)
        time.sleep(duration)


def job(
    envs: Dict[str, Any],
    infile: TextIO,
    tasks: List[str],
    show_only: bool,
    duration: float,
    loop: bool = False,
) -> None:
    recipe = parse_recipe(infile, envs)
    if not tasks:
        tasks = recipe.keys()
    if show_only:
        for key in tasks:
            print(key)
        return
    for t in tasks:
        if t not in recipe.keys():
            raise NotImplementedError
    if loop:
        while True:
            job_(recipe, tasks, duration)
    else:
        job_(recipe, tasks, duration)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--recipefile", "-r", type=argparse.FileType("r"), required=True
    )
    parser.add_argument("--envfile", "-e", type=argparse.FileType("r"))
    parser.add_argument("--task", "-t", type=str, nargs="+", default=[])
    parser.add_argument("--loop", "-l", type=bool, default=False)
    parser.add_argument("--debug", type=bool, default=False)
    parser.add_argument("--show", type=bool, default=False)
    parser.add_argument("--duration", type=float, default=0.0)
    d = parser.parse_args()
    _set_logger(d.debug)
    if d.envfile is not None:
        envs = yaml.safe_load(d.envfile)
    else:
        envs = {}
    if not d.loop:
        job(envs, d.recipefile, d.task, d.show, d.duration)
    else:
        job(envs, d.recipefile, d.task, d.show, d.duration, loop=True)


if __name__ == "__main__":
    main()
