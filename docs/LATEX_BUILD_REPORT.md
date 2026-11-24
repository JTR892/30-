# LaTeX构建与PDF核验报告

**状态：已通过。**  
**核验日期：2026-11-25**  
**源代码提交：** `53f33b2289993f9b0a5ba5653e19529a64b17578`  
**GitHub Actions运行：** [45462673176](https://github.com/JTR892/30-/actions/runs/45462673176)  
**Artifact：** `manuscript-pdf`，ID `14954220922`  
**PDF：** `paper/main.pdf`，3页，A4，PDF 1.7  
**本次已下载PDF SHA-256：** `605788d9fdc298fb681590ca7285bbfb30d8e066279370f2bd5903f9facc17b1`

## 验收结果

| 检查项 | 结果 | 证据 |
|---|---|---|
| Python 3.10测试 | 通过 | Actions job conclusion=success |
| Python 3.11测试 | 通过 | Actions job conclusion=success |
| Python 3.12测试 | 通过 | Actions job conclusion=success |
| Python 3.13测试 | 通过 | Actions job conclusion=success |
| 引用键预检查 | 通过 | 6个被引用键均存在于19条BibTeX记录中 |
| XeLaTeX编译 | 通过 | `latexmk: All targets (main.xdv main.pdf) are up-to-date` |
| BibTeX | 通过 | 生成并载入`main.bbl`；PDF参考文献区显示6条被引用文献 |
| 未解析引用检查 | 通过 | 编译后检查`main.log`未发现未解析citation/reference |
| PDF生成 | 通过 | `main.pdf`非空，3页A4 |
| Artifact上传 | 通过 | Actions日志确认Artifact成功上传 |
| 页面检查 | 通过 | 下载PDF并逐页查看：标题、摘要、公式、流程图、表格、参考文献均可读 |
| 排版复核 | 通过 | 将流程图移至完整K-means说明段之后；节点标签换行；最终编译日志无Overfull/Underfull hbox记录 |

## 失败原因与修复

最初失败版本在第62行将`C_s`和`\Delta_s`直接写在正文数学模式之外，触发`Missing $ inserted`。该错误导致第一轮LaTeX运行未能正常进入BibTeX解析流程，因此出现未解析引用提示。

修复为`$C_s$`与`$\Delta_s$`，随后增加以下CI检查：
1. 编译前自动比对`main.tex`的引用键与`references.bib`条目；
2. 编译后要求`main.pdf`与`main.bbl`均非空；
3. 检查最终`main.log`中不存在未解析引用/交叉引用。

首次成功编译后，人工逐页检查发现流程图浮动位置不理想且节点标签有宽度警告。随后将流程图移动到完整K-means段落之后，并将`Baseline/Attention`改为分行显示，再次编译、下载和逐页核验。

## 交付说明

- PDF通过GitHub Actions Artifact提供，不把CI构建产物误称为真实实验结果。
- Artifact保留期限在后续CI配置中设为90天；已完成的本次Artifact仍按运行时原有保留期限管理。
- 这份PDF是论文结构骨架，不是论文初稿或实验结果。结果表保留占位符，未编造任何指标。
- CI成功只证明软件测试和论文构建通过；不证明真实数据审计、M1 Max模型训练或聚类实验已完成。
