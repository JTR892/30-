# 核心相关工作 12 篇 · 2026-11-22

总台账保留 17 条。下表选 12 条支撑三层主线，其余 5 条为背景/实现备查。核验深度不等于全文复现；截至本次核验不能宣称穷尽检索或世界首次。


| 文献 / 标识 | 任务 / 数据 | 方法 / 指标 | 局限 | 本题推进 | 核验深度 |
|---|---|---|---|---|---|
| L01 [On the effect of the attention mechanism for automatic welding defects detection based on deep learning](https://doi.org/10.1016/j.eswa.2025.126386)；10.1016/j.eswa.2025.126386 | 焊缝缺陷/无缺陷监督二分类；15,194 张平衡图像；T91 管 DWDI | CNN 对照通道注意力和空间注意力；特征/显著性分析；Accuracy、漏检率 MD、误报率 FA | 不能据监督二分类或 t-SNE 分离推断无监督多缺陷聚类有效 | 目标域不使用缺陷类别训练，比较高维几何与缺陷/来源信息依赖；规模作为受控因素 | 2026-11-22；本地全文已读；Crossref 元数据 HTTP 200；出版社/DOI 浏览访问受限 |
| L02 [Anomaly Clustering: Grouping Images into Coherent Clusters of Anomaly Types](https://arxiv.org/abs/2112.11573)；arXiv:2112.11573 | 工业异常类型聚类；MVTec AD 与 Magnetic Tile Defect | 预训练局部特征加权汇聚；无监督/少量正常标签两种设置；NMI、ARI、F1 | 与本题最接近；局部特征加权聚合已有先例，且正常标签版本含额外监督 | 对照已有局部加权聚类，并检验几何变化的缺陷语义依据；不称首次异常聚类 | 2026-11-22；官方会议页与全文已核对；PDF HTTP 200 |
| L03 [RIAWELC: A Novel Dataset of Radiographic Images for Automatic Weld Defects Classification](https://doi.org/10.53375/ijecer.2023.320)；10.53375/ijecer.2023.320 | 焊缝四类监督分类及数据集；24,407 个 224×224 图块；CR/PO/LP/ND | 裁块及增强；迁移学习定制 SqueezeNet；分类 Accuracy、混淆矩阵 | 图块不等同独立整幅焊缝图；不能直接当作跨域整图等价对照 | 候选外部数据；先核验源图分组和使用条款，明确裁块单位差异 | 2026-11-22；期刊页及 5 页 PDF 经 web 打开；本机 urllib 证书错误另记 |
| L05 [CBAM: Convolutional Block Attention Module](https://arxiv.org/abs/1807.06521)；arXiv:1807.06521 | 图像识别与检测的注意力模块；ImageNet-1K、MS COCO 等 | 通道注意力后接空间注意力；池化、卷积和门控；Top-1/Top-5 error、检测 AP | 完整 CBAM 包括两种分支；只用空间分支不能冒称新 CBAM 或完整复现 | 固定实现与插入位置；模块机制是已知结构，本文检验其信息依赖，不提出新门控 | 2026-11-22；arXiv 摘要及全文已读；PDF 已下载 |
| L06 [Deep Residual Learning for Image Recognition](https://arxiv.org/abs/1512.03385)；arXiv:1512.03385 | 残差图像识别网络；ImageNet、CIFAR-10 等 | 残差学习与深层卷积骨干；Top-1/Top-5 error 等 | 原始识别任务结果不代表本机训练速度或焊缝聚类有效性 | 选择 ResNet18 作为受控骨干；预训练权重版本与监督来源须披露 | 2026-11-22；arXiv 元数据/摘要已核对；不引用未核查的实验数值 |
| L07 [A Simple Framework for Contrastive Learning of Visual Representations](https://proceedings.mlr.press/v119/chen20j.html)；arXiv:2002.05709 | 对比自监督表示学习；ImageNet 及迁移评价数据 | 双视图增强、投影头、对比损失；研究 batch/增强影响；线性评价与迁移分类准确率 | 自然图像增强/大 batch 经验不能直接移植低对比焊缝 | 区分增强一致性与跨图像缺陷语义；以统一训练和三层评价检验 | 2026-11-22；PMLR 与 arXiv 全文已核对；PDF HTTP 200 |
| L08 [Momentum Contrast for Unsupervised Visual Representation Learning](https://arxiv.org/abs/1911.05722)；arXiv:1911.05722 | 对比自监督表示学习；ImageNet；下游视觉任务 | 动量编码器与特征队列；线性评价准确率、下游检测/分割指标 | 队列缓解字典大小约束，但不是免费解决焊缝增强与 MPS 适配 | 只作为预实验失败时的全矩阵替代；不可按测试结果混选算法 | 2026-11-22；arXiv/CVF 信息与全文已核对；PDF HTTP 200 |
| L12 [An expert knowledge-empowered CNN approach for welding radiographic image recognition](https://research.polyu.edu.hk/en/publications/an-expert-knowledge-empowered-cnn-approach-for-welding-radiograph/)；10.1016/j.aei.2023.101963 | 小样本焊缝射线图像识别；摘要未给出可完整复核的数据划分细节 | 去模糊与亮度调整自监督任务，辅助 CNN 识别；摘要报告 F1；不移用数值设定本题目标 | 仅核验作者机构元数据和摘要，未取得全文；不能评论其未知的实验细节 | 否定“焊缝小样本自监督此前无人研究”的宽泛创新声明 | 2026-11-22；PolyU 作者机构条目/DOI/摘要已核对；全文未获取 |
| L13 [Understanding Contrastive Representation Learning through Alignment and Uniformity on the Hypersphere](https://proceedings.mlr.press/v119/wang20k.html)；arXiv:2005.10242 | 对比表征学习解释；摘要描述视觉/语言实验；未核查具体划分 | 从正样本对齐与归一化表征分布均匀性分析对比学习；alignment、uniformity 与下游任务；不移用数值 | 增强正样本对齐不等于真实缺陷类别内紧致；本文焊缝语义需另检验 | 在原始高维空间计算缺陷类别几何与跨来源近邻，排查退化 | 2026-11-22；PMLR 原始元数据、摘要和 BibTeX 已打开；尚未精读全文 |
| L14 [Sanity Checks for Saliency Maps](https://proceedings.neurips.cc/paper/2018/hash/294a8ed24b1ad22ec2e7efea049b8737-Abstract.html)；arXiv:1810.03292 | 显著性解释可靠性检验；摘要未详列数据划分；不推断 | 检验部分显著性解释对模型与数据的依赖；解释是否反映模型/数据的检验；细节待全文核对 | 结论针对所检验的显著性方法，不能直接断言 CBAM 门控无效 | 区域图只作关联证据，加入匹配扰动与来源诊断；聚类归因目标另定义 | 2026-11-22；NeurIPS 官方摘要和作者/会议元数据已打开；尚未精读全文 |
| L15 [Shortcut Learning in Deep Neural Networks](https://arxiv.org/abs/2004.07780)；10.1038/s42256-020-00257-z | 捷径学习与泛化问题的观点分析；观点文章，不当作焊缝实验数据 | 讨论标准评价有效而条件变化时失效的决策线索；非统一新基准；不引用未知实验数值 | 不能据此证明本数据存在捷径，或声称模型已经去除混杂 | 核验类别×来源覆盖，进行来源内与跨来源诊断；缺失证据不冒充曝光记录 | 2026-11-22；作者 arXiv 摘要、作者与关联期刊 DOI 已打开；尚未精读全文 |
| L16 [Interpretable Explanations of Black Boxes by Meaningful Perturbation](https://arxiv.org/abs/1704.03296)；10.1109/ICCV.2017.371; arXiv:1704.03296 | 基于扰动的模型解释；原任务为分类器解释；摘要未详列划分 | 用显式、可解释的图像扰动研究决策依赖；扰动解释的可检验性；不移用未知数值 | 分类决策不等于无分类头的聚类；扰动伪影与语义改变需单独控制 | 预定缺陷/背景匹配扰动，冻结中心，报告特征与分配变化；不在测试上学习解释掩膜 | 2026-11-22；CVF 直开返回 403；作者 arXiv 元数据、摘要与关联 DOI 已打开；尚未精读全文 |


核心 12 条均附 DOI/arXiv。L13–L16 仅依已核验的原始摘要/元数据引用方法论动机，未知实验细节不写入。指标参考 L17 留在总台账，未核实 DOI/arXiv，使用 JMLR 稳定卷页与官方链接，不编造标识。
