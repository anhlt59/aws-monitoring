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
	@bash ops/development/install.sh
activate: ## Activate the virtual environment
	@bash ops/development/activate.sh

# RUNNING ========================================================================
start: ## Start the local master server
	@bash ops/development/start.sh
start-master: ## Start the local master server
	pnpm exec sls offline start --stage local --config serverless.master.local.yml
start-agent: ## Start the local agent server
	pnpm exec sls offline start --stage local --config serverless.agent.local.yml

# PREPARE ========================================================================
prepare-neos: ## Prepare s3 and iam roles for NEOS environment
	@bash ops/deployment/prepare.sh neos

# DEPLOYMENT ========================================================================
deploy-local: ## Deploy to the local environment
	@bash ops/deployment/deploy.sh local master
	@bash ops/deployment/deploy.sh local agent
deploy-neos: ## Deploy to the NEOS environment
	@bash ops/deployment/deploy.sh neos master
	@bash ops/deployment/deploy.sh neos agent

# PACKAGING ========================================================================
package-local: ## Create artifacts for local deployment
	@bash ops/deployment/package.sh local
package-neos: ## Create artifacts for NEOS deployment
	@bash ops/deployment/package.sh neos

# DELETE ===========================================================================
delete-local: ## Delete the local deployment
	@bash ops/deployment/delete.sh local agent
	@bash ops/deployment/delete.sh local master
delete-neos: ## Delete the NEOS deployment
	@bash ops/deployment/delete.sh neos agent
	@bash ops/deployment/delete.sh neos master

# TESTING ==========================================================================
test: ## Run the tests
	@pytest --cov=src tests/

coverage: ## Check code coverage
	@coverage run --source src -m pytest
	@coverage report -m
	#@coverage html && $(BROWSER) htmlcov/index.html
