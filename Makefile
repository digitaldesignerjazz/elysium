.PHONY: push status syntax

MSG ?=

push:
	@if [ -z "$(MSG)" ]; then echo 'Nutzung: make push MSG="typ: nachricht"'; exit 2; fi
	@bash scripts/git-push.sh "$(MSG)"

status:
	@git status -sb

syntax:
	@python3 -m py_compile agents/aura/cycle.py
	@python3 -m py_compile ai-swarm/core/vector_memory.py
	@python3 -m py_compile code-examples/agent-scheduler/xcoin_payment_scheduler.py
	@echo syntax ok
