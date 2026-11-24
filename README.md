# 焊缝 X 射线裁剪图像空间注意力研究

[![CI](https://github.com/JTR892/30-/actions/workflows/ci.yml/badge.svg)](https://github.com/JTR892/30-/actions/workflows/ci.yml)

工作题目：**有限无标签训练数据下空间注意力对焊缝 X 射线裁剪图像表征与无监督聚类的影响**。

本研究以团队现有 15,194 张焊缝 X 射线二分类裁剪图像为目标数据集。该数量来自研究者确认，实际可读、去重后的数量须以本地审计为准。数据来自团队 DR_SD 数据，并对应 Wang 等 2025 年论文所用数据；不将其称为新数据集。

## v0.3 研究边界
- 观察单位：一张从完整底片裁剪得到的焊缝区域图像。
- 参考类别：缺陷 / 无缺陷。
- 不要求追溯原始底片或焊口编号；不要求先完成全部 XML 核验。
- 必须检查图像可读性、显式类别目录映射、SHA256 完全重复和冲突标签。
- 图像级划分不能证明原始底片/焊口级独立性，不能声称跨底片泛化。
- XML 仅为后续扩展；未核验前不承诺缺陷区域分析。

## 核心问题
1. 10%、50%、100% 无标签训练数据规模下，空间注意力是否改变缺陷/无缺陷聚类表现？
2. 聚类变化是否对应特征几何与聚类稳定性的变化？

## 实验
- Baseline：ResNet18 + SimCLR。
- Attention：相同模型增加一个 CBAM 空间注意力分支（不是完整 CBAM）。
- 主聚类 K-means，固定 K=2。K 来自已知二分类任务定义，属于已知簇数条件下的无监督聚类。
- 主指标 ARI；辅助 AMI、NMI、Silhouette、稳定性、类内/类间距离、kNN purity。
- 目标矩阵：3 个规模 × 2 个模型 × 5 个配对种子 = 30 次；预算不足可用 3 个种子、18 次，并标为探索性。
- 训练子集从训练分区随机嵌套抽样，不用标签抽样；配对模型使用同一子集。

## 一个月初稿计划
个人月度计划：**2026-11-20 至 2026-12-20**，当前处于数据处理阶段。逐日任务、阶段验收、风险和延期处理见 [docs/ONE_MONTH_MANUSCRIPT_PLAN.md](docs/ONE_MONTH_MANUSCRIPT_PLAN.md)。该计划是任务安排，完成状态必须由真实产物证明。

## 自动化检查
GitHub Actions 在 push、pull request 和手动触发时执行：
- Python 合成数据测试与 DRAFT 协议门槛检查；
- XeLaTeX 论文编译，并将 PDF 作为 workflow artifact 保存。

查看 [Actions](https://github.com/JTR892/30-/actions) 获取真实运行结果。CI 只验证代码和论文能否构建，不代表真实数据或模型实验通过。

## 本地数据与算力任务
复制 `config/label_map.example.json` 为 `config/label_map.local.json`，将键改成真实类别目录名。然后执行：
```sh
make install
make audit DATA_ROOT="/actual/binary_dataset"
make split
make test
make paper
```
M1 Max 环境检查与合成数据 MPS 冒烟测试：
```sh
python -m pip install -r requirements-mps.txt
make environment
make mps-smoke
```
详细步骤见 [docs/LOCAL_EXECUTION.md](docs/LOCAL_EXECUTION.md)。

原始图像、真实路径、标签映射、数据清单、测试标签和训练产物不得上传公开 GitHub。仓库已忽略常用本地文件，但仍需检查 `git status`，不要使用 `git add -f` 强制上传。

## 状态
已实现只读审计、显式标签映射、SHA256 重复检查、图像级分层划分与协议门槛。真实数据审计仍需在本地数据上执行。MPS smoke 脚本仅测试合成数据吞吐；正式 SimCLR/Attention 训练器尚未实现，正式训练不得启动。仓库不是已训练成功的流水线。

测试：`python -m unittest discover -s tests -v`。LaTeX：在 `paper` 目录运行 `latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex`。
