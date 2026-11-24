# 六项交付与验收 v0.3 · 2026-11-24

| 要求 | 当前材料 | 状态 |
|---|---|---|
| 研究问题、数据、方法、指标、风险 | docs/RESEARCH_BRIEF.md、docs/ANALYSIS_PLAN.md | 两个核心问题；已知K=2、标签隔离和图像级划分限制明确；无真实发现 |
| GitHub骨架与AGENTS | README、AGENTS、protocol | 审计/标签映射/重复检查/图像级划分/协议门槛已实现；训练代码未实现 |
| 自动化测试 | .github/workflows/ci.yml | GitHub Actions run #2已通过，Python 3.10—3.13全部成功 |
| LaTeX构建 | .github/workflows/ci.yml、paper/main.tex | XeLaTeX已成功编译；PDF artifact已上传，保留至2026-12-08 |
| 真实数据与算力 | docs/LOCAL_EXECUTION.md、mps_smoke.py | 本地审计与MPS合成smoke工具已准备；真实数据和M1 Max尚未执行 |
| 正式训练与分析 | docs/TRAINING_IMPLEMENTATION_PLAN.md | SimCLR/Attention训练器尚未实现，参数未冻结，不得声称已训练 |
| 一个月初稿计划 | docs/ONE_MONTH_MANUSCRIPT_PLAN.md | 已建立2026-11-20至2026-12-20逐日任务表；当前数据处理阶段，任务完成情况以产物证据回填 |

CI运行记录：https://github.com/JTR892/30-/actions/runs/45390330753

合成测试只验证代码逻辑，不代表真实数据或模型效果。MPS smoke使用随机合成图像，不代表真实训练吞吐。DRAFT协议应拒绝正式训练。
