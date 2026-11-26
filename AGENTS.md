# Research agreement v0.5 · audit revision 2026-11-27

## Objective
Study how spatial attention affects multiclass clustering of supplied weld-region radiographs, including researcher-confirmed normal images and reviewed defect types. Compare low/mid/high unlabeled training sizes, with counts and final taxonomy pending qualification. Examine representation geometry, stability and, where evidence permits, defect versus source/acquisition reliance. This is empirical work, not a new attention algorithm or a demonstrated causal mechanism.

## Evidence discipline
- Never invent counts, paths, metrics, citations, logs, permissions or publication/sync status. Separate measured facts, researcher statements, literature claims, designs and hypotheses.
- Raw industrial images, XML, user literature PDFs, real paths, filenames, hashes and private manifests stay outside public Git. Publish code and aggregate conclusions only.
- A full structural audit is not professional defect-label certification. Missing XML is not a normal label; good=qualified is a researcher statement until supported by producer records. Weld region is provisionally auxiliary, not a defect type. Other-defect labels remain heterogeneous until defined.
- Retain negative/null findings, conflicts and audit history. Do not fix labels, resize boxes or remove original files silently.
- Pixel-unique files are not independent welds. The same weld/source film/duplicate component must stay in one partition. Unknown provenance must remain unknown; do not replace this with image-only random splitting and call it independent.
- No defect labels in representation training or main training-subset selection. Disclose externally supervised pretraining and any label-assisted audit/preprocessing decisions.
- No training, PCA/K-means fitting, checkpoint selection or tuning on a frozen final test. This receipt was a prepartition audit of all supplied directories, including their labels; the supplied train/val/test folders are not an untouched final test.
- Before data-dependent pilots, freeze a separate pilot protocol defining allowable training/cluster-fit images and prohibiting final-test access. Freeze the final protocol after pilot evidence and before final runs. Current gates are not passed.
- Heatmaps, geometry and perturbation are different evidence levels. They alone do not prove a causal mechanism. Mean gray level is not measured exposure. Dimensions alone do not establish crop lineage.

## Current evidence and entrypoints
- Local receipt/audit exists; actual path is only in ignored `config/paths.local.json`.
- Versioned private outputs: `reports/audit/`; all image/XML records, figures and detailed issues remain ignored.
- Public aggregate: `docs/DATA_AUDIT_2026-11-27.md`; code review: `docs/CODE_REVIEW_2026-11-27.md`.
- `python -m weldstudy.xml_audit --root /actual/root --config config/xml_audit.local.json --out reports/audit/NEW_VERSION`
- `python scripts/verify_xml_audit.py --root /actual/root --audit reports/audit/VERSION`
- `python scripts/check_content_overlap.py --root /actual/root --audit reports/audit/VERSION` (limited candidate search, not full near-duplicate/provenance verification).
- `python -m unittest discover -s tests -v`
- `python -m weldstudy.protocol --config config/protocol.json` (current DRAFT must exit 2).
- `make split` and the legacy split CLI are disabled for the active study. The old binary helper API is retained only for historical synthetic tests, not authorized formal partitioning.
- `config/protocol.legacy_v0.4.json` is archival. Active config is v0.5 DRAFT, with taxonomy/K/budgets unset and qualification gates false.
- Training, geometry and semantic-analysis pipelines are not implemented or validated. Synthetic tests are not real performance evidence.
- Manuscript: `paper/main.tex`; build `latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex` in `paper/`. Generic skeleton, not official journal template.

## Verification and change control
Run relevant tests after audit/split changes. Preserve audit versions, label dictionaries, exclusions, seeds, coordinate conventions and scripts/hashes. Interpret the current envelope rejection as a provisional continuous-coordinate check: equal endpoints may mean one pixel under an inclusive convention. Do not silently convert conventions.

A final protocol requires reviewed taxonomy, source-connected groups, duplicate/near-duplicate resolution, permission, valid pilot and training implementation, frozen split and analysis, and locked final evaluation. Administrative flags do not substitute for reviewed artifacts. Post-test changes are exploratory and cannot overwrite primary results.

Every literature update must synchronize registry, relevant comparison table, bibliography/manuscript to the authorized GitHub repository as applicable; verify the remote commit and report failure. Organization status and access/reading depth are distinct. For L06 and L13–L17 retain existing records and do not revisit solely for additional verification unless the user changes that instruction.
