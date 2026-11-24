# Research agreement v0.4

## Working title
不同训练数据规模下空间注意力对焊缝X射线裁剪图像自监督表征学习与无监督聚类表现的影响

This is a working title, not a claim of novelty or a result.

## Objective
Evaluate whether adding a spatial-attention branch to a fixed self-supervised contrastive representation pipeline changes known-K clustering performance as the number of distinct target-domain training images changes. Examine whether any observed difference is accompanied by changes in feature geometry or clustering stability.

## Evidence and provenance discipline
Keep these evidence categories separate:
- **Researcher-reported:** the team has a binary weld-radiograph image collection labelled DR_SD; the intended target count is 15,194; the researcher associates it with the dataset used in Wang et al. (2025); the working sample unit is one cropped weld-region image and the researcher believes these images were cropped from complete films.
- **Literature-confirmed:** Wang et al. (2025) reports 15,194 digital X-ray images, balanced between defective and non-defective images, collected using a flat-panel detector for T91 pipe butt joints (55 mm) with DWDI exposure. The article itself also discusses attention and separation of defective/non-defective feature clusters. DOI: https://doi.org/10.1016/j.eswa.2025.126386
- **Not independently verified locally:** exact one-to-one identity between the team's files and the article's 15,194 images; the local crop lineage and original-film mapping; actual on-disk/readable/unique count; permission for public redistribution. Equal counts do not prove identical files.
Never upgrade a researcher-reported or unverified fact into an audited fact.

## Data contract
- Observation unit: one cropped weld-region X-ray image, not a complete radiographic film and not a defect bounding box.
- Working binary labels: defect / no_defect. Actual folder names must be mapped explicitly.
- The target count 15,194 is an expected count, not an audited count.
- The current audit code maps the first directory below DATA_ROOT to a label. DATA_ROOT therefore needs to be the parent of the two class folders. If the actual structure differs, adapt and test the audit code rather than renaming or moving original data.
- Original-film, weld-ID, and source-group mapping are not required for the primary image-level study. Do not claim film-level independence or unseen-film generalization.
- Before splitting, audit readability, explicit folder-to-label mapping, SHA256 exact duplicates, and conflicting labels.
- Same-content/same-label files may be deterministically collapsed and logged. Same-content/different-label files are a hard failure. Hashes do not detect all near-duplicates or crops from shared films.
- XML matching and annotation validation are optional follow-up, not a main-experiment gate.

## Label-use boundary
- Use labels for one stratified image-level 80/10/10 train / cluster-fit / test partition; disclose that stratification uses labels.
- The repository currently names the cluster-fitting partition "calibration" for compatibility. In research prose call it "聚类拟合集（代码目录名 calibration）" to avoid implying probability calibration.
- Train, cluster-fit, and test image manifests must not contain labels. Store test labels separately and lock them operationally.
- Representation training reads pixels only. Training-size subsets are random nested samples from train, not label-stratified.
- Labels are not used for representation training, subset selection, checkpoint/hyperparameter selection, K-means fitting, or cluster assignment.
- After the analysis protocol is frozen and test labels are opened, labels may be used for ARI / AMI / NMI, class-conditional feature geometry, and kNN purity as post-hoc evaluation only. These diagnostics must not feed back into model selection.
- Primary K=2 is specified by the known binary task. Disclose known-K unsupervised clustering; do not give labels or cluster-class mapping to K-means.

## Model and evidence
- Baseline: ResNet18 + SimCLR.
- Attention: same setup plus one CBAM spatial branch; do not call it full CBAM or a new attention method.
- The configured initialization is paired ImageNet-supervised ResNet18 weights. If retained, describe the target-domain training as self-supervised contrastive training with externally supervised ImageNet initialization; do not call the entire pipeline fully unsupervised end-to-end.
- Same paired images, backbone initialization, update budget, batch, optimizer, schedule, and augmentation for both variants.
- Fixed optimizer steps control update count, not total compute: the attention branch adds computation, and smaller subsets repeat images more often. Report wall time, memory, parameter/FLOP differences if measured, unique image count, and image exposures. Interpret the experiment as a fixed-update-budget comparison of unique target-data scale, not as a pure causal effect of sample count.
- Report actual counts, repeat exposures, wall time, memory, all seeds, failures and negative results.
- Silhouette, stability, heatmaps, or 2-D plots alone do not prove defect semantics or causality.
- Image-level split plus exact deduplication does not establish source-film independence.
- Never invent counts, paths, metrics, citations, logs, or completion status.

## Planned primary analysis
For seed s and training ratio r, define Δ_s(r) = ARI_attention,s(r) - ARI_baseline,s(r).
Primary low-vs-full-scale contrast: C_s = Δ_s(10%) - Δ_s(100%). Positive C_s means the relative ARI advantage of attention is larger at 10% than at 100%; it does not by itself mean attention is beneficial at either scale.
Secondary summary: A_s = mean of Δ_s(10%), Δ_s(50%), and Δ_s(100%).
Report each seed and descriptive summaries. With three or five seeds, avoid unsupported claims of statistical significance.

## Entrypoints
- Install: make install
- Audit: make audit DATA_ROOT=/actual/binary_dataset
- Split: make split
- MPS environment: make environment
- Synthetic MPS smoke: install requirements-mps.txt, then make mps-smoke
- Gate: python -m weldstudy.protocol --config config/protocol.json
- Tests: make test or python -m unittest discover -s tests -v
- Manuscript: make paper or run latexmk in paper/
- GitHub CI: .github/workflows/ci.yml runs tests and LaTeX compilation on GitHub-hosted runners.

## Change control
Synthetic tests do not validate real data/model performance. MPS synthetic throughput is not SimCLR/attention throughput. Before final training freeze split and label-map hashes, preprocessing, training parameters, K=2, checkpoint rule, analysis plan hash, and code version. Test labels are opened only after freeze. The full SimCLR/attention trainer is not yet implemented; do not claim model training is available until it exists and passes tests.

## Security
The repository is public. Do not configure a self-hosted M1 runner for untrusted pull-request workflows. Keep real data and local execution on the workstation; do not upload raw data or private manifests as workflow artifacts.
