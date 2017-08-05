# Bamboo Crawler

A Hobby Crawler.
It is almost under construction.

# Usage

## Installatino

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
      metadata: {}
  process:
    type: HTTPCrawler
  output:
    type: StdoutOutputter
```

# License

BSD-3-Clause
