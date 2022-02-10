docs:
	cd docs
	make html
isort:
	isort web
typecheck:
	mypy web --ignore-missing-imports

reformat:
	black web
	black tests

test:
	pytest -v tests --cov web --cov-report xml --asyncio-mode auto

precommit: isort reformat typecheck
