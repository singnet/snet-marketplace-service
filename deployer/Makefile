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

LOG_LEVEL ?= DEBUG

test:
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