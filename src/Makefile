###
# Run
###

run_dev:
	uvicorn app.vkbot:app --host 0.0.0.0 --port 8000 --reload

run_prod:
	uvicorn app.vkbot:app --host 0.0.0.0 --port 8000 --log-level warning

###
# Linter Tests
###

radon:
	poetry run radon mi -s -n B .

flake:
	poetry run flake8

bandit:
	poetry run bandit -r app

mypy:
	poetry run mypy .

isort:
	poetry run isort .
isort_ci:
	poetry run isort --diff

black:
	poetry run black .
black_ci:
	poetry run black --diff

ltest: black isort flake bandit radon
ltest_ci: black_ci isort_ci flake bandit radon
