# Research agreement

## Objective
Study how spatial attention affects whole-image weld radiograph clustering through three linked questions: clustering performance, representation geometry, and reliance on defect information versus acquisition/source cues. Vary unlabeled target-domain training size as a controlled experimental factor. This is an empirical study, not a claim of a new attention mechanism or an established causal explanation.

## Evidence rules
- Never invent data counts, paths, metrics, citations, training logs or GitHub publication status.
- Distinguish observed facts, literature claims, design decisions and hypotheses.
- Raw industrial images and user-supplied literature PDFs must remain outside Git.
- No training, PCA, K-means fitting, checkpoint selection or hyperparameter tuning on final test images or labels.
- Same weld/source-film/duplicate component must stay in one partition. Unknown labels are not normal labels.
- No defect labels in representation training or main training-subset selection. Any supervised pretraining must be disclosed.
- Preserve unfavorable and null results. Never write results sections from expected effects.
- Geometry, attention overlap and perturbation responses are different evidence levels. Heatmaps and metric correlations alone do not establish a causal mechanism. Missing exposure records must not be replaced by mean gray level and called measured exposure.

## Paths
- Workspace root: this repository.
- Raw industrial radiograph dataset: **not supplied**. Set `config/paths.local.json` after receipt; do not invent a path.
- Audit outputs: local `reports/audit/`; schema: `data/manifests/schema.csv`.
- Group mapping: a locally supplied CSV with `image_id,group_id`, based on verified acquisition/weld provenance.
- Protocol: `config/protocol.json`; local environment probe: `reports/environment.local.json`.
- Research charter and six-item acceptance: `docs/RESEARCH_BRIEF.md` and `docs/DELIVERABLES.md`.
- Geometry/semantic analysis definitions: `docs/ANALYSIS_PLAN.md`; evidence availability: `docs/RESOURCES.md`.
- Manuscript: `paper/main.tex`; bibliography: `paper/references.bib` (generic article skeleton, not an official journal template).
- Paper build: `latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex` in `paper/`.

## Implemented code entrypoints
- `python -m weldstudy.environment --out reports/environment.local.json`
- `python -m weldstudy.audit --root /actual/data/root --out reports/audit`
- `python -m weldstudy.split --manifest reports/audit/manifest.csv --groups /actual/groups.csv --out data/splits`
- `python -m weldstudy.protocol --config config/protocol.json`
- `python -m unittest discover -s tests -v`

Model training and geometry/semantic analysis are not implemented at this stage. Do not describe this scaffold as a completed or validated SimCLR pipeline. Before implementing a data-dependent pilot, audit the data and freeze a separate pilot protocol with test access prohibited. Minimal synthetic MPS smoke tests and synthetic software checks may precede that freeze. Use training/calibration evidence from pilots to specify the final protocol; freeze the final protocol before final runs or opening test labels. The current CLI gates the final protocol only and does not authorize pilots.

## Verification and change control
Run relevant tests after changing audit/split semantics. Test fixtures are synthetic and cannot establish real data availability or model performance. Keep label taxonomy, exclusions, seeds, cluster-count rule and protocol version in an audit trail. Any post-test changes must be labeled exploratory and must not overwrite the frozen primary analysis.

Every literature update must be synchronized to the authorized GitHub repository, including the literature registry, relevant comparison table, bibliography or manuscript as applicable. Verify the remote commit and report any sync failure. Record organization status separately from actual access and reading depth; never describe abstract-only work as full-text review. For L06 and L13–L17, retain existing records and do not revisit the papers solely for further verification unless the user changes this instruction.

