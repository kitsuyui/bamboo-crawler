.PHONY: lint
lint: flake8 mypy check_import_order check_format

.PHONY: test
test: pytest

.PHONY: format
format: isort black pyupgrade

.PHONY: isort
isort:
	isort bamboo_crawler tests

.PHONY: black
black:
	black bamboo_crawler tests

.PHONY: flake8
flake8:
	flake8 bamboo_crawler tests

.PHONY: pyupgrade
pyupgrade:
	pyupgrade --py37-plus bamboo_crawler/*.py bamboo_crawler/*.py

.PHONY: mypy
mypy:
	mypy bamboo_crawler tests

.PHONY: check_import_order
check_import_order:
	isort --check-only --diff bamboo_crawler tests

.PHONY: check_format
check_format:
	black --check bamboo_crawler tests

.PHONY: pytest
pytest:
	pytest --cov=bamboo_crawler tests --doctest-modules --cov-report=xml

.PHONY: build
build:
	python3 -m build .

.PHONY: clean
clean:
	rm -rf *.egg-info dist
