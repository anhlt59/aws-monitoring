.PHONY: help active install coverage test bootstrap deploy package destroy
.DEFAULT_GOAL := help
stage         := local

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
install: ## Install the packages.
	@bash ops/development/install.sh
activate: ## Activate the virtual environment.
	@bash ops/development/activate.sh

# RUNNING ========================================================================
start: ## Start the local server.
	@bash ops/development/start.sh

# BOOTSTRAP ========================================================================
bootstrap: ## Prepare s3 and iam roles.
	@bash ops/deployment/bootstrap.sh $(stage)

# DEPLOYMENT ========================================================================
deploy: ## Deploy to the $stage environment.
	@bash ops/deployment/deploy.sh $(stage)

# PACKAGING ========================================================================
package: ## Create artifacts for deployment.
	@bash ops/deployment/package.sh $(stage)

# DESTROY ===========================================================================
destroy: ## Destroy a deployment.
	@bash ops/deployment/destroy.sh $(stage)

# TESTING ==========================================================================
test: ## Run the tests.
	@cd backend && pytest --cov=src tests/
coverage: ## Check code coverage.
	@bash ops/development/coverage.sh
