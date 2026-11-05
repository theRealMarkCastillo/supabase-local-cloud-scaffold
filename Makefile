.PHONY: init up down check smoke test logs admin origin frontend migration migrate
init:
	python3 scripts/stack.py init
up:
	python3 scripts/stack.py up
down:
	python3 scripts/stack.py down
check:
	python3 scripts/stack.py check
smoke:
	python3 scripts/smoke.py
test:
	python3 -m unittest discover -s tests -v
logs:
	python3 scripts/stack.py logs
admin:
	python3 scripts/stack.py admin
origin:
	python3 scripts/stack.py origin "$(URL)"
frontend:
	python3 scripts/stack.py frontend "$(KIND)"
migration:
	python3 scripts/migrations.py new "$(NAME)"
migrate:
	python3 scripts/stack.py migrate

function:
	python3 scripts/functions.py new "$(NAME)"

integration:
	python3 tests/integration_migrations.py
