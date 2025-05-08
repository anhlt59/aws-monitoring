.PHONY: help active install coverage test start-master start-agent deploy-agent deploy-master
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys
from urllib.request import pathname2url
webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys
for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

# =================================================================================
help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)
install: ## Install the packages
	@bash ops/scripts/development/install.sh
activate: ## Activate the virtual environment
	@bash ops/scripts/development/activate.sh

# RUNNING ========================================================================
start: ## Start the local master server
	@bash ops/scripts/development/start.sh

# DEPLOYMENT ========================================================================
deploy-local: ## Deploy to the local environment
	@bash ops/scripts/deployment/deploy.sh local
deploy-neos: ## Deploy to the NEOS environment
	@bash ops/scripts/deployment/deploy.sh neos

# PACKAGING ========================================================================
package-local: ## Create artifacts for local deployment
	@bash ops/scripts/deployment/package.sh local
package-neos: ## Create artifacts for NEOS deployment
	@bash ops/scripts/deployment/package.sh neos

# DELETE ===========================================================================
delete-local: ## Delete the local deployment
	@bash ops/scripts/deployment/delete.sh local
delete-neos: ## Delete the NEOS deployment
	@bash ops/scripts/deployment/delete.sh neos

# TESTING ==========================================================================
test: ## Run the tests
	@pytest --cov=src tests/

coverage: ## Check code coverage
	@coverage run --source src -m pytest
	@coverage report -m
	#@coverage html && $(BROWSER) htmlcov/index.html
