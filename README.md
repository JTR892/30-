# 焊缝X射线裁剪图像自监督表征与聚类研究

[![CI](https://github.com/JTR892/30-/actions/workflows/ci.yml/badge.svg)](https://github.com/JTR892/30-/actions/workflows/ci.yml)

**工作题目：不同训练数据规模下空间注意力对焊缝X射线裁剪图像自监督表征学习与无监督聚类表现的影响。**

本研究拟使用团队现有、标记为DR_SD的焊缝X射线二分类图像。研究者报告目标数量为15,194张，并认为其与Wang等（2025）论文所用数据相对应。Wang等论文确实报告15,194张数字X射线图像且缺陷/非缺陷数量平衡，但团队本地文件与论文数据的逐文件身份对应、裁剪来源链及实际可用数量尚未独立核验。不得仅凭数量相同宣称文件完全一致。论文DOI：https://doi.org/10.1016/j.eswa.2025.126386

## v0.4研究边界
- 观察单位：一张焊缝区域X射线裁剪图像，不是完整底片或缺陷框。
- 当前工作标签：缺陷 / 无缺陷；实际目录名必须显式映射。
- 15,194是目标数量，不是本地审计确认的可用数量。
- 原始底片、焊口和来源组映射不是主实验硬性要求；图像级划分不能证明底片级独立性，不能声称跨底片泛化。
- XML只作为后续扩展；未完成匹配、坐标、类别与一致性核验前，不承诺缺陷区域分析。
- 当前审计脚本按DATA_ROOT下的第一层目录映射类别；运行前确认DATA_ROOT直接包含两个类别目录。如实际目录层级不同，先修改并测试脚本，不要改动原始数据。

## 核心问题
1. 在train划分内部使用10%、50%、100%的无标签图像子集时，空间注意力是否改变缺陷/无缺陷聚类表现？
2. 注意力带来的聚类变化是否伴随特征几何和聚类稳定性的变化？

## 预设实验
- Baseline：ResNet18 + SimCLR。
- Attention：相同训练设置增加一个CBAM空间注意力分支；不是完整CBAM，也不是新注意力算法。
- 两模型计划使用相同的ImageNet监督预训练ResNet18初始化。目标数据上的对比训练不使用缺陷/无缺陷标签；因此准确表述为“目标域自监督训练 + 外部监督预训练初始化”，不能称整个流程完全无监督。
- 训练比例10%、50%、100%均以train划分为分母，不是全体15,194张的比例；子集在train内随机嵌套抽样且不按标签分层。
- 聚类使用K-means，固定K=2。K来自已知二分类任务，属于已知簇数条件下的无监督聚类，不是发现未知缺陷类别数。
- ARI为主要外部指标；AMI、NMI为辅助外部指标；Silhouette为内部结构指标；特征几何、kNN purity和聚类稳定性作为事后诊断。
- 主对比为C_s = [ARI_attention(10%) - ARI_baseline(10%)] - [ARI_attention(100%) - ARI_baseline(100%)]。同时报告50%结果和各规模原始配对差。
- 固定优化步数和batch用于控制更新次数；较小子集会被重复采样更多次。必须记录曝光次数、耗时与内存，结论不能被表述为纯粹的样本数量因果效应。

## 30天初稿详细计划
个人计划周期：2026-11-20至2026-12-20。11月20日为Day 0启动基线，11月21日至12月20日为Day 1至Day 30；首尾日期均列出时有31个日期标签，但实际经过30天。详见[30天初稿详细计划（11.20—12.20）](docs/ONE_MONTH_MANUSCRIPT_PLAN.md)。

## 自动化检查
GitHub Actions在push、pull request和手动触发时执行：
- Python合成数据测试与DRAFT协议门槛检查；
- XeLaTeX论文编译，并将PDF作为workflow artifact保存。

CI只验证代码和论文能否构建，不代表真实数据审计、M1 Max训练或模型实验通过。查看[Actions](https://github.com/JTR892/30-/actions)获取运行结果。

## 本地数据与算力任务
复制config/label_map.example.json为config/label_map.local.json，将键改成真实类别目录名。确认DATA_ROOT直接包含两个类别目录后执行：

    make install
    make audit DATA_ROOT="/actual/binary_dataset"
    make split
    make test
    make paper

M1 Max环境检查与合成数据MPS冒烟测试：

    python -m pip install -r requirements-mps.txt
    make environment
    make mps-smoke

合成MPS smoke仅使用随机合成图像与普通ResNet18，不代表SimCLR双视图+空间注意力的真实训练吞吐。详细步骤见docs/LOCAL_EXECUTION.md。

原始图像、真实路径、标签映射、数据清单、测试标签和训练产物不得上传公开GitHub。

## 当前状态
已实现只读审计、显式标签映射、SHA256完全重复检查、图像级分层划分与协议门槛。真实数据审计仍需在本地执行。MPS smoke仅测试合成数据吞吐；正式SimCLR/Attention训练器尚未实现。当前没有真实模型训练结果。
