# 七天验收与 2026-12-17 整稿计划 v0.2

Dates use Asia/Shanghai. The first-day kickoff package is delivered; later dates below are a plan, not a record of completed experiments. Raw data availability is a critical dependency.

| Date | Reviewable artifact | Acceptance condition |
|---|---|---|
| 2026-11-22 | 六项材料 v0.2、三层分析与论文骨架 | 问题/证据/代码状态一致；结果占位；合成测试和编译通过 |
| 2026-11-23 | 真实 manifest 与语义证据可得性表 | 目录到位；类别、位置、形态、来源、设备、曝光缺失逐项记录 |
| 2026-11-24 | 类别字典、来源组、固定划分和独立预实验协议 | 无组跨区；测试隔离；训练侧标注格式与诊断范围核验；预实验范围先冻结 |
| 2026-11-25 | 合成 MPS 前反向、训练侧尺寸/batch 与扰动样例 | 同步计时、内存；无静默 CPU 回退；缺陷可见性与扰动人工痕迹核验 |
| 2026-11-26 | 两模型可比性、特征/门控导出、分析代码合成验证 | 公共权重一致；几何、来源、区域诊断输入/输出定义；实现状态单列 |
| 2026-11-27 | 四组短学习预实验、固定特征参照、三层分析试运行 | 只用训练/校准；检查坍缩、计算量和分析可估计性；测试标签未开启 |
| 2026-11-28 | 最终配置/三层分析冻结、资格报告与预算 | 主效应、距离/kNN/稳定性/扰动参数和规范哈希；门槛通过后选 30 或探索性 18 次 |
| 2026-11-29–30 | Clean-environment rerun and recovery instructions | Pipeline produces traceable artifacts |
| 2026-12-01–08 | Full paired experiment matrix | Preserve all seeds and failures under frozen protocol |
| 2026-12-09–10 | 三层证据表：ARI/AMI/NMI、几何/稳定性、来源及合资格扰动 | 按冻结计划解封评价；不拟合/调参；报告来源与分析覆盖及两类不确定性 |
| 2026-12-11–13 | 按问题—方法—真实发现—解释组织完整初稿 | 结果对应真实日志；区域/几何/来源证据核对，不预设正效应 |
| 2026-12-14–15 | Targeted supplementary analyses and revision | Mark new analyses exploratory; retain primary results |
| 2026-12-16 | Final integrity/reproducibility review | Check references, leakage, numbers and figures |
| 2026-12-17 | Final manuscript and reproducibility package | Submit only the actually completed research scope |

If the data gate is not met by November 24, revise scope and dates rather than inventing a complete experimental paper. A null or negative effect remains reportable; no publication acceptance is promised.

三层诊断主要复用模型，但须单列后处理与人工核验预算。缺少语义证据时收缩题目/解释；不能把预定机制分析全部推迟到看结果后再挑选。
