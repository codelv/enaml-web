docs:
	cd docs
	make html
isort:
	isort web
	isort tests
typecheck:
	mypy web --ignore-missing-imports
lintcheck:
	flake8 --ignore=E203,E266,E501,W503,E731 web
	flake8 --ignore=E203,E266,E501,W503,E731 tests
reformat:
	black web
	black tests
test:
	pytest -v tests --cov web --cov-report xml --asyncio-mode auto

precommit: isort reformat typecheck lintcheck
