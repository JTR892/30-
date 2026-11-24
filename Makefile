.PHONY: install test paper audit split environment mps-deps mps-smoke

PYTHON ?= python
LABEL_MAP ?= config/label_map.local.json
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

audit:
	@test -n "$(DATA_ROOT)" || (echo "Usage: make audit DATA_ROOT=/absolute/path/to/binary_dataset" && exit 2)
	@test -f "$(LABEL_MAP)" || (echo "Missing label map: $(LABEL_MAP). Copy config/label_map.example.json and edit it." && exit 2)
	$(PYTHON) -m weldstudy.audit --root "$(DATA_ROOT)" --label-map "$(LABEL_MAP)" --out "$(AUDIT_OUT)"

split:
	@test -f "$(AUDIT_OUT)/manifest.csv" || (echo "Missing $(AUDIT_OUT)/manifest.csv; run make audit first." && exit 2)
	$(PYTHON) -m weldstudy.split --manifest "$(AUDIT_OUT)/manifest.csv" --out "$(SPLIT_OUT)" --seed 17

environment:
	mkdir -p reports/local
	$(PYTHON) -m weldstudy.environment --out reports/local/environment.json

mps-deps:
	$(PYTHON) -m pip install -r requirements-mps.txt

mps-smoke:
	$(PYTHON) -m weldstudy.mps_smoke --batch-size $(MPS_BATCH_SIZE) --image-size $(MPS_IMAGE_SIZE) --steps $(MPS_STEPS) --out reports/local/mps_smoke.json
