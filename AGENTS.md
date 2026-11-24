# Research agreement v0.3

## Objective
Study whether a spatial-attention branch changes self-supervised representation and known-K unsupervised clustering of cropped weld radiographs as unlabeled training size changes. The target dataset is the team's existing 15,194-image binary DR_SD crop dataset, associated by the researcher with the dataset used in Wang et al. (2025). This is a target count, not an audited on-disk count.

## Data contract
- Observation unit: one cropped weld-region X-ray image, not a full film or a defect box.
- Labels: defect / no_defect.
- Original-film, weld-ID, and source-group mapping are not required.
- Do not claim film-level independence or unseen-film generalization. Image-level splitting may place related crops in different partitions.
- Before splitting, audit readability, explicit folder-to-label mapping, SHA256 exact duplicates, and conflicting labels.
- Same-content/same-label files may be deterministically collapsed and logged. Same-content/different-label files are a hard failure. Hashes do not detect all near-duplicates.
- XML validation is optional follow-up, not a main-experiment gate.
- Raw images, local paths, label maps, local manifests, test labels, checkpoints and reports must stay outside public Git.

## Label-use boundary
- Use labels for one stratified image-level 80/10/10 train/calibration/test partition; disclose this.
- Train/calibration/test image manifests must not contain labels. Store test labels separately and lock them.
- Representation training reads pixels only. Training-size subsets are random nested samples from train, not label-stratified.
- Labels are not used for representation training, subset selection, checkpoint/hyperparameter selection, K-means fitting, or cluster assignment.
- Labels are used for final ARI/AMI/NMI and class-conditional descriptive analyses only.
- Primary K=2 is specified by the known binary task. Disclose known-K unsupervised clustering; do not give labels or cluster-class mapping to K-means.

## Model and evidence
- Baseline: ResNet18 + SimCLR.
- Attention: same setup plus one CBAM spatial branch; do not call it full CBAM or a new attention method.
- Disclose ImageNet supervised pretraining if used.
- Same paired images, initialization policy, update budget, batch, optimizer, schedule, and augmentation for both variants.
- Report actual counts, repeat exposures, wall time, memory, all seeds, failures and negative results.
- Silhouette/stability/heatmaps alone do not prove defect semantics or causality.
- Image-level split plus exact deduplication does not establish source-film independence.
- Never invent counts, paths, metrics, citations, logs, or completion status.

## Entrypoints
- Install: `make install`
- Audit: `make audit DATA_ROOT=/actual/binary_dataset`
- Split: `make split`
- MPS environment: `make environment`
- Synthetic MPS smoke: install `requirements-mps.txt`, then `make mps-smoke`
- Gate: `python -m weldstudy.protocol --config config/protocol.json`
- Tests: `make test` or `python -m unittest discover -s tests -v`
- Manuscript: `make paper` or run latexmk in `paper/`
- GitHub CI: `.github/workflows/ci.yml` runs tests and LaTeX compilation on GitHub-hosted runners.

## Change control
Synthetic tests do not validate real data/model performance. MPS synthetic throughput is not SimCLR throughput. Before final training freeze split and label-map hashes, preprocessing, training parameters, K=2, checkpoint rule, analysis plan hash, and code version. Test labels are opened only after freeze. The full SimCLR/attention trainer is not yet implemented; do not claim model training is available until it exists and passes tests.

## Security
The repository is public. Do not configure a self-hosted M1 runner for untrusted pull-request workflows. Keep real data and local execution on the workstation; do not upload raw data or private manifests as workflow artifacts.
