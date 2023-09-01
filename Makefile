SHELL := /bin/bash
.SHELLFLAGS = -ec
.ONESHELL:
.SILENT:

.PHONY: help
help:
	grep -E '^\.PHONY: [a-zA-Z0-9_-]+ .*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = "(: |##)"}; {printf "\033[36m%-30s\033[0m %s\n", $$2, $$3}'

.PHONY: build-venv ## Create virtual environment
build-venv:
	echo "Creating python3 virtual environment with poetry"
	python3 -m venv .venv
	source .venv/bin/activate
	pip install -r requirements.txt

.PHONY: clean-venv ## Remove virtual environment
clean-venv:
	echo "Cleaning venv"
	rm -rf .venv

.PHONY: clean ## Clean the folder and subfolders
clean:
	echo "Cleaning folder"
	find . -maxdepth 1 -type f -name "*coverage*" -not -name "coverage.svg" -o -name "flake*" -delete
	find . -maxdepth 2 -type d -name .pytest_cache -o -name .venv -o -name docs -o -name __pycache__ -o -name html | xargs rm -rf
