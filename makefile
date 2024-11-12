docs:
	cd docs
	make html
isort:
	isort web tests
lintcheck:
	flake8 --ignore=E501,W503,E226  web tests
typecheck:
	mypy web --ignore-missing-imports

reformat:
	black web tests
test:
	pytest -v tests --cov web --cov-report xml --asyncio-mode auto

precommit: isort reformat lintcheck typecheck
