# Research agreement

## Objective
Study whether reducing unlabeled target-domain training data changes the benefit of spatial attention for whole-image weld radiograph clustering. This is an empirical study, not a claim of a new attention mechanism.

## Evidence rules
- Never invent data counts, paths, metrics, citations, training logs or GitHub publication status.
- Distinguish observed facts, literature claims, design decisions and hypotheses.
- Raw industrial images and user-supplied literature PDFs must remain outside Git.
- No training, PCA, K-means fitting, checkpoint selection or hyperparameter tuning on final test images or labels.
- Same weld/source-film/duplicate component must stay in one partition. Unknown labels are not normal labels.
- No defect labels in representation training or main training-subset selection. Any supervised pretraining must be disclosed.
- Preserve unfavorable and null results. Never write results sections from expected effects.

## Paths
- Workspace root: this repository.
- Raw industrial radiograph dataset: **not supplied**. Set `config/paths.local.json` after receipt; do not invent a path.
- Audit outputs: local `reports/audit/`; schema: `data/manifests/schema.csv`.
- Group mapping: a locally supplied CSV with `image_id,group_id`, based on verified acquisition/weld provenance.
- Protocol: `config/protocol.json`; local environment probe: `reports/environment.local.json`.
- Manuscript: `paper/main.tex`; bibliography: `paper/references.bib` (generic article skeleton, not an official journal template).
- Paper build: `latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex` in `paper/`.

## Implemented code entrypoints
- `python -m weldstudy.environment --out reports/environment.local.json`
- `python -m weldstudy.audit --root /actual/data/root --out reports/audit`
- `python -m weldstudy.split --manifest reports/audit/manifest.csv --groups /actual/groups.csv --out data/splits`
- `python -m weldstudy.protocol --config config/protocol.json`
- `python -m unittest discover -s tests -v`

Model training is not implemented at this kickoff stage. Do not describe this scaffold as a completed or validated SimCLR pipeline. Implement training only after data audit, MPS smoke test and protocol freeze.

## Verification and change control
Run relevant tests after changing audit/split semantics. Test fixtures are synthetic and cannot establish real data availability or model performance. Keep label taxonomy, exclusions, seeds, cluster-count rule and protocol version in an audit trail. Any post-test changes must be labeled exploratory and must not overwrite the frozen primary analysis.

