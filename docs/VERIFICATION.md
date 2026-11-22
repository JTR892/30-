# v0.2 验证记录 · 2026-11-22

| 检查 | 实际结果 | 支持范围 |
|---|---|---|
| `python -m unittest discover -s tests -v` | 10 项通过 | 合成审计/来源划分与最终协议门槛；不代表真实数据或模型性能 |
| DRAFT 配置检查 | 返回码 2，ready_for_training=false | 未填参数、数据/MPS/标签锁定和分析门槛均未冒充通过 |
| 文献台账与 BibTeX | 17 个唯一键完全对应；正文引用键存在 | 引用完整性，不等于所有全文已读 |
| 核心相关工作表 | 12 条，均有 DOI/arXiv，记录日期与深度 | 满足核心条目结构；L17 指标参考另以期刊卷页保留 |
| Markdown 本地链接 | 检查通过 | 当前 README/docs 的相对链接目标存在 |
| `latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex` | 成功，5 页；最终日志无未定义引用和 Overfull | 论文骨架可构建，不包含真实结果 |
| PDF 排版 | PDFium 渲染五页总览及流程图页目检通过 | 中文/图中文字可见，无观察到的图中文字重叠；本机 Poppler 缺 Adobe-GB1 CMap，未将其空白渲染误称通过 |
| `git diff --check` | 通过 | 未发现补丁空白错误 |

原始数据审计、MPS 训练、正式参数、三层分析实现与研究结果均未完成。仓库同步状态以实际 Git 历史和远端分支为准，本页不预填尚未生成的提交哈希。
