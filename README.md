# 焊缝 X 射线裁剪图像空间注意力研究

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

## 本地数据流程
复制 `config/label_map.example.json` 为 `config/label_map.local.json`，将键改成真实类别目录名：
```sh
python -m weldstudy.audit --root /actual/binary_dataset --label-map config/label_map.local.json --out reports/audit
python -m weldstudy.split --manifest reports/audit/manifest.csv --out data/splits --seed 17
```
路径只是命令格式示例。原始图像、真实路径、标签映射和本地审计产物不得上传公开 GitHub。

## 状态
已实现只读审计、显式标签映射、SHA256 重复检查、图像级分层划分与协议门槛。真实数据审计、MPS 训练吞吐、模型训练和几何分析仍未完成。仓库是研究骨架，不是已训练成功的流水线。

运行合成测试：`python -m unittest discover -s tests -v`。LaTeX：在 paper 目录运行 `latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex`。
