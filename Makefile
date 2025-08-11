.PHONY: help active install coverage test start-master start-agent \
	bootstrap-neos bootstrap-cm \
	deploy-local deploy-neos deploy-cm \
	package-local package-neos package-cm \
	destroy-local destroy-neos destroy-cm
.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys
for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

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

# BOOTSTRAP ========================================================================
bootstrap-neos: ## Prepare s3 and iam roles for NEOS environment
	@bash ops/deployment/bootstrap.sh neos agent
bootstrap-cm: ## Prepare s3 and iam roles for CM+ environment
	@bash ops/deployment/bootstrap.sh cm master
	@bash ops/deployment/bootstrap.sh cm-stg agent

# DEPLOYMENT ========================================================================
deploy-local: ## Deploy to the local environment
	@bash ops/deployment/deploy.sh local master
	@bash ops/deployment/deploy.sh local agent
deploy-neos: ## Deploy to the NEOS environment
	@bash ops/deployment/deploy.sh neos agent
deploy-cm: ## Deploy to the CM+ environment
	@bash ops/deployment/deploy.sh cm master
	@bash ops/deployment/deploy.sh cm-stg agent

# PACKAGING ========================================================================
package-local: ## Create artifacts for local deployment
	@bash ops/deployment/package.sh local
package-neos: ## Create artifacts for NEOS deployment
	@bash ops/deployment/package.sh neos
package-cm: ## Create artifacts for CM+ deployment
	@bash ops/deployment/package.sh cm

# DESTROY ===========================================================================
destroy-local: ## Destroy the local deployment
	@bash ops/deployment/destroy.sh local agent
	@bash ops/deployment/destroy.sh local master
destroy-neos: ## Destroy the NEOS deployment
	@bash ops/deployment/destroy.sh neos agent
	@bash ops/deployment/destroy.sh neos master
destroy-cm: ## Destroy the CM+ deployment
	@bash ops/deployment/destroy.sh cm-stg agent
	@bash ops/deployment/destroy.sh cm master

# TESTING ==========================================================================
test: ## Run the tests
	@pytest --cov=src tests/

coverage: ## Check code coverage
	@bash ops/development/coverage.sh
