.PHONY: help active install
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
	@bash ops/install.sh
activate: ## Activate the virtual environment.
	@bash ops/activate.sh
