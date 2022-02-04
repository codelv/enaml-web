docs:
	cd docs
	make html
isort:
	isort atomdb
typecheck:
	mypy atomdb --ignore-missing-imports

reformat:
	black atomdb
	black tests

test:
	pytest -v tests --cov atomdb --cov-report xml --asyncio-mode auto

precommit: isort reformat typecheck
