# Project checkpoint — 2026-11-22

Research question and constraints are preserved in AGENTS.md and docs/protocol.md. The industrial dataset path, annotation schema, provenance groups and use permission are pending. This public repository contains no raw industrial files or private machine paths.

Implemented: read-only inventory, environment probe, provenance-group split, nested subsets with fixed calibration/test partitions, draft-protocol gate and six synthetic-fixture tests. Tests passed locally; this is not a model-training result.

Literature: 12 adopted records in docs/literature.json, with DOI/arXiv, verification date and access depth. An abstract-only record is explicitly marked; blocked publisher access is recorded rather than called successful. Literature metadata verification is not a guarantee that the research question has no prior work.

Paper: paper/main.tex and references.bib. General article skeleton, not a journal-approved template. Results remain placeholders. Compiled successfully with XeLaTeX and the desktop editor compiler; 4-page PDF. The source includes a placeholder diagram, empty results and 12 bibliography entries.

Next: finish artifact verification, freeze the protocol only after real data and throughput audits, then implement and run the training pipeline. Do not present future steps as completed experiments.
