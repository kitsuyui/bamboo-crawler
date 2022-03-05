# Bamboo Crawler

[![codecov](https://codecov.io/gh/kitsuyui/bamboo-crawler/branch/master/graph/badge.svg?token=s7NTzwl5fl)](https://codecov.io/gh/kitsuyui/bamboo-crawler)
[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![PyPI version shields.io](https://img.shields.io/pypi/v/bamboo-crawler.svg)](https://pypi.python.org/pypi/bamboo-crawler/)

A Hobby Crawler.
It is almost under construction.

# Usage

## Installation

```console
$ pip install bamboo-crawler
```

## Run

```
$ bamboo --recipe recipe.yml
```

## Recipe

```YAML
mytask:
  input:
    type: ConstantInputter
    options:
      value: http://httpbin.org/robots.txt
  process:
    type: HTTPCrawler
  output:
    type: StdoutOutputter
```

# License

BSD-3-Clause License
