run:
	@serverless offline --stage example --noAuth
.PHONY: run

lint:
	@ruff check . --fix
	@ruff format .
.PHONY: lint