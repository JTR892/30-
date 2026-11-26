.PHONY: install test paper audit audit-xml split environment mps-deps mps-smoke

PYTHON ?= python
LABEL_MAP ?= config/label_map.local.json
AUDIT_CONFIG ?= config/xml_audit.local.json
AUDIT_OUT ?= reports/audit
SPLIT_OUT ?= data/splits
MPS_BATCH_SIZE ?= 4
MPS_IMAGE_SIZE ?= 128
MPS_STEPS ?= 10

install:
	$(PYTHON) -m pip install -e .

test:
	$(PYTHON) -m unittest discover -s tests -v

paper:
	cd paper && latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex

audit: audit-xml

audit-xml:
	@test -n "$(DATA_ROOT)" || (echo "Set DATA_ROOT to the received dataset directory" && exit 2)
	@test -f "$(AUDIT_CONFIG)" || (echo "Create a reviewed local XML audit configuration from config/xml_audit.example.json" && exit 2)
	$(PYTHON) -m weldstudy.xml_audit --root "$(DATA_ROOT)" --config "$(AUDIT_CONFIG)" --out "$(AUDIT_OUT)"

split:
	@echo "Formal splitting is blocked: resolve multiclass taxonomy, duplicate/source components and semantic review first. Legacy v0.4 image-only splitter is not authorized."
	@exit 2

environment:
	mkdir -p reports/local
	$(PYTHON) -m weldstudy.environment --out reports/local/environment.json

mps-deps:
	$(PYTHON) -m pip install -r requirements-mps.txt

mps-smoke:
	$(PYTHON) -m weldstudy.mps_smoke --batch-size $(MPS_BATCH_SIZE) --image-size $(MPS_IMAGE_SIZE) --steps $(MPS_STEPS) --out reports/local/mps_smoke.json
