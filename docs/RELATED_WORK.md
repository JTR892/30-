# 核心相关工作12篇 · 更新于2026-11-25

总台账保留19条，其中12条为核心对照，其余7条为背景/实现备查。19条均已完成现有信息的基础整理；这不表示均已精读全文。

## 与本研究定位直接相关的先行工作

**L01 Wang et al. (2025)**：[On the effect of the attention mechanism for automatic welding defects detection based on deep learning](https://doi.org/10.1016/j.eswa.2025.126386)，Expert Systems with Applications 268, 126386。

该论文报告15,194张数字X射线图像，缺陷与非缺陷数量相等；数据来自T91管对接接头的DWDI数字射线采集。论文在二分类检测网络中比较通道注意力和空间注意力，并从特征可视化/量化、显著像素及缺陷与非缺陷特征簇等角度分析注意力作用。

**对本研究的约束：**不能声称首次在焊缝X射线图像使用空间注意力，也不能声称首次分析缺陷/非缺陷特征簇。本文拟区分的研究设定是：目标域缺陷/非缺陷标签不参与SimCLR表征训练，并把train划分内的训练图像规模作为受控变量，评价已知K=2聚类、特征几何和稳定性。是否形成足够增量贡献仍待完整文献排重与实验验证。

**数据身份边界：**论文报告15,194张图像，与团队数据目标数量相同；研究者报告本地数据与该论文数据相对应。但数量相同不等于逐文件相同，本地文件级对应和裁剪来源链尚未独立核验。

## 核心文献台账

| 文献 / 标识 | 任务 / 数据 | 方法 / 指标 | 局限 | 本题推进 | 核验深度 |
|---|---|---|---|---|---|
| L01 [On the effect of the attention mechanism for automatic welding defects detection based on deep learning](https://doi.org/10.1016/j.eswa.2025.126386)；10.1016/j.eswa.2025.126386 | 焊缝缺陷/无缺陷监督二分类；论文报告15,194张平衡数字X射线图像；T91管、DWDI | CNN对照通道/空间注意力；特征与显著像素分析；Accuracy、漏检率MD、误报率FA；原文也讨论两类特征簇 | 已覆盖焊缝空间注意力与特征簇分析；监督分类不能直接回答目标域标签不参与表征训练时的训练规模问题 | 研究问题限定为目标域自监督训练和train子集规模控制；不称首次 | 2026-11-25；原文摘要和数据/训练段落可访问；本地文件身份未核验 |
| L02 [Anomaly Clustering: Grouping Images into Coherent Clusters of Anomaly Types](https://arxiv.org/abs/2112.11573)；arXiv:2112.11573 | 工业异常类型聚类；MVTec AD与Magnetic Tile Defect | 预训练局部特征加权汇聚；NMI、ARI、F1 | 与本题最接近；局部特征加权聚类已有先例 | 对照已有局部加权聚类，不称首次异常聚类 | 2026-11-22；官方会议页与全文已核对 |
| L03 [RIAWELC: A Novel Dataset of Radiographic Images for Automatic Weld Defects Classification](https://doi.org/10.53375/ijecer.2023.320)；10.53375/ijecer.2023.320 | 焊缝四类监督分类；24,407个224×224图块 | 裁块及增强；迁移学习分类 | 图块不等同独立整幅焊缝图 | 外部候选数据，先核验许可和样本单位 | 2026-11-22；期刊页及PDF已打开 |
| L05 [CBAM: Convolutional Block Attention Module](https://arxiv.org/abs/1807.06521)；arXiv:1807.06521 | 图像识别与检测 | 通道注意力后接空间注意力；池化、卷积和门控 | 只用空间分支不能冒称完整CBAM | 固定空间分支实现，不提出新门控 | 2026-11-22；arXiv全文已读 |
| L07 [A Simple Framework for Contrastive Learning of Visual Representations](https://proceedings.mlr.press/v119/chen20j.html)；arXiv:2002.05709 | 对比自监督表示学习 | 双视图增强、投影头、对比损失 | 自然图像增强/大batch经验不能直接移植低对比焊缝 | 审查焊缝增强，统一训练设置 | 2026-11-22；PMLR与arXiv全文已核对 |
| L12 [An expert knowledge-empowered CNN approach for welding radiographic image recognition](https://research.polyu.edu.hk/en/publications/an-expert-knowledge-empowered-cnn-approach-for-welding-radiograph/)；10.1016/j.aei.2023.101963 | 小样本焊缝射线图像识别；2,154张64×64缺陷区域图像，四类 | 自监督重建预处理后迁移到监督分类；Acc、Precision、Recall、F1 | 分类阶段使用标签；图块与整图单位不同 | 对照自监督预训练与目标域标签隔离 | 2026-11-23；核对指定章节和表格，非逐字全文精读 |
| L13 [Understanding Contrastive Representation Learning through Alignment and Uniformity on the Hypersphere](https://proceedings.mlr.press/v119/wang20k.html)；arXiv:2005.10242 | 对比表征学习解释 | alignment、uniformity | 不能直接推断焊缝语义聚类 | 辅助解释几何变化 | 2026-11-22；摘要/元数据已核对，未精读全文 |
| L14 [Sanity Checks for Saliency Maps](https://proceedings.neurips.cc/paper/2018/hash/294a8ed24b1ad22ec2e7efea049b8737-Abstract.html)；arXiv:1810.03292 | 显著性解释可靠性 | 模型/数据依赖检验 | 不直接证明CBAM门控无效 | 热图仅作关联证据 | 2026-11-22；摘要和元数据已核对 |
| L15 [Shortcut Learning in Deep Neural Networks](https://arxiv.org/abs/2004.07780)；10.1038/s42256-020-00257-z | 捷径学习观点分析 | 讨论条件变化下的泛化风险 | 不能据此证明本数据存在捷径 | 作为来源混杂风险背景 | 2026-11-22；摘要和DOI已核对 |
| L16 [Interpretable Explanations of Black Boxes by Meaningful Perturbation](https://arxiv.org/abs/1704.03296)；10.1109/ICCV.2017.371 | 基于扰动的模型解释 | 显式图像扰动 | 分类决策不等于聚类；扰动伪影需控制 | 如做扰动分析，预先定义扰动规则 | 2026-11-22；arXiv摘要/元数据已打开 |
| L18 [A weld defect segmentation framework based on visual self-supervised learning](https://doi.org/10.1080/10589759.2025.2595520)；10.1080/10589759.2025.2595520 | 焊缝X射线缺陷分割；RTWD | 对象级掩码自监督预训练与多头分割 | 专家标注参与训练；分割不同于整图聚类 | 区分像素级监督与目标域自监督聚类 | 2026-11-23；核对指定章节，非逐字全文精读 |
| L19 [An unsupervised welding quality detection method based on high-quality condition-guided diffusion reconstruction](https://doi.org/10.1016/j.jmapro.2026.01.059)；10.1016/j.jmapro.2026.01.059 | 焊缝X射线无监督异常检测与定位 | 条件引导扩散重建；像素AUROC/AP | 异常检测/定位不是缺陷类型聚类 | 明确任务和指标不可混同 | 2026-11-23；核对指定章节与表格，非逐字全文精读 |

其余文献的阅读深度和限制仍见docs/LITERATURE_ACCESS.md。不得把摘要/元数据核验表述为全文精读。
