PYTHON ?= .venv-tools/bin/python

.PHONY: init up down check smoke test logs admin origin frontend migration migrate
init: tools
	$(PYTHON) scripts/stack.py init
up: tools
	$(PYTHON) scripts/stack.py up
down: tools
	$(PYTHON) scripts/stack.py down
check: tools
	$(PYTHON) scripts/stack.py check
smoke: tools
	$(PYTHON) scripts/smoke.py
test: tools
	$(PYTHON) -m unittest discover -s tests -v
logs: tools
	$(PYTHON) scripts/stack.py logs
admin: tools
	$(PYTHON) scripts/stack.py admin
origin: tools
	$(PYTHON) scripts/stack.py origin "$(URL)"
frontend: tools
	$(PYTHON) scripts/stack.py frontend "$(KIND)"
migration: tools
	$(PYTHON) scripts/migrations.py new "$(NAME)"
migrate: tools
	$(PYTHON) scripts/stack.py migrate

function: tools
	$(PYTHON) scripts/functions.py new "$(NAME)"

integration: tools
	$(PYTHON) tests/integration_migrations.py

frontend-test: tools
	node --test web/tests/session-state.test.mjs

.PHONY: tools frontend-test browser-test
tools:
	python3 scripts/setup_tools.py

browser-test: tools
	node tests/browser-account-switch.mjs

.PHONY: tunnel tunnel-set
tunnel:
	python3 scripts/tunnel.py
tunnel-set: origin
