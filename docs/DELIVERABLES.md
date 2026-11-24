# 六项交付与验收 v0.4 · 2026-11-25

| 要求 | 当前材料 | 状态 |
|---|---|---|
| 研究问题、数据、方法、指标、风险 | docs/RESEARCH_BRIEF.md、docs/ANALYSIS_PLAN.md | 已修订概念和标签边界；无真实发现 |
| GitHub骨架与AGENTS | README、AGENTS、protocol | 审计/标签映射/重复检查/图像级划分/协议门槛已实现；训练代码未实现 |
| 自动化测试 | .github/workflows/ci.yml | v0.4的Python 3.10、3.11、3.12、3.13测试全部通过 |
| LaTeX构建 | .github/workflows/ci.yml、paper/main.tex | v0.4 XeLaTeX编译通过；6个引用键全部匹配19条文献记录；PDF已上传Artifact并完成逐页检查，见docs/LATEX_BUILD_REPORT.md |
| 真实数据与算力 | docs/LOCAL_EXECUTION.md、mps_smoke.py | 本地审计与MPS合成smoke工具已准备；真实数据和M1 Max尚未执行 |
| 正式训练与分析 | docs/TRAINING_IMPLEMENTATION_PLAN.md | SimCLR/Attention训练器尚未实现，参数未冻结，不得声称已训练 |
| 30天初稿详细计划 | docs/ONE_MONTH_MANUSCRIPT_PLAN.md | 11.20—12.20计划已按Day 0至Day 30重排；当前仍处于数据处理阶段，状态须由产物证据回填 |

研究计划自检记录见docs/PLAN_REVIEW_CHANGELOG.md。CI合成测试不代表真实数据或模型效果。DRAFT协议应拒绝正式训练。
