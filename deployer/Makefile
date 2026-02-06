run:
ifeq ($(OS),Windows_NT)
	@powershell -Command "$$env:LOG_LEVEL='DEBUG'; $$env:IS_SERVERLESS_OFFLINE='true'; serverless offline --stage example --noAuth"
else
	@export LOG_LEVEL=DEBUG && \
	export IS_SERVERLESS_OFFLINE=true && \
	serverless offline --stage example --noAuth
endif
.PHONY: run

lint:
	@ruff check . --fix
	@ruff format .
.PHONY: lint

check-docker:
	@echo Checking Docker status...
ifeq ($(OS),Windows_NT)
	@docker info > NUL 2>&1 || (echo ERROR: Docker daemon is not running. Please start Docker and try again. && exit 1)
else
	@docker info > /dev/null 2>&1 || (echo ERROR: Docker daemon is not running. Please start Docker and try again. && exit 1)
endif
	@echo Docker is running.
.PHONY: check-docker

LOG_LEVEL ?= DEBUG

test: check-docker
ifeq ($(OS),Windows_NT)
	@powershell -Command " \
		$$env:LOG_LEVEL='$(LOG_LEVEL)'; \
		$$env:IS_SERVERLESS_OFFLINE='true'; \
		python -m coverage run -m pytest tests/ -v; \
		python -m coverage report \
	"
else
	@export LOG_LEVEL=$(LOG_LEVEL) && \
	export IS_SERVERLESS_OFFLINE=true && \
	python -m coverage run -m pytest tests/ -v && \
	python -m coverage report
endif
.PHONY: test