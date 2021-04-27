SHELL = /usr/bin/env bash -xeuo pipefail

lint:
	python -m flake8 src/ && python -m isort src/

install:
	python -m pip install --upgrade pip
	python -m pip install -r requirements.txt

build:
	@sam build \
		--template-file sam.template.yml \
		--use-container

deploy: build
	@sam deploy

.PHONY: lint install build deploy
