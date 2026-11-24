# 六项交付与验收 v0.3 · 2026-11-24

| 要求 | 当前材料 | 状态 |
|---|---|---|
| 研究问题、数据、方法、指标、风险 | RESEARCH_BRIEF.md、ANALYSIS_PLAN.md | 两个核心问题；已知 K=2、标签隔离和图像级划分限制明确；无真实发现 |
| GitHub骨架与 AGENTS | README、AGENTS、protocol | 审计/标签映射/重复检查/图像级划分/协议门槛已实现；训练代码未实现 |
| 自动化测试 | .github/workflows/ci.yml | 已配置 Python 多版本合成测试与 DRAFT 门槛检查；等待首次运行结果 |
| LaTeX构建 | .github/workflows/ci.yml、paper/main.tex | 已配置 XeLaTeX 云端编译与 PDF artifact；等待首次运行结果 |
| 真实数据与算力 | docs/LOCAL_EXECUTION.md、mps_smoke.py | 本地审计与 MPS 合成 smoke 工具已准备；真实数据和 M1 Max 尚未执行 |
| 正式训练与分析 | docs/TRAINING_IMPLEMENTATION_PLAN.md | SimCLR/Attention 训练器尚未实现，参数未冻结，不得声称已训练 |

合成测试只验证代码逻辑，不代表真实数据或模型效果。MPS smoke 使用随机合成图像，不代表真实训练吞吐。DRAFT协议应拒绝正式训练。
