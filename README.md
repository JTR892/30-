# 焊缝射线图像空间注意力研究

Weld radiograph attention study

工作题目：**有限数据条件下空间注意力对焊缝 X 射线图像无监督聚类的影响与表征机制分析**。

研究问题：目标域缺陷类别标签不参与训练时，空间注意力如何改变整幅图像的聚类性能、表征几何与缺陷/来源信息依赖？数据规模是检验这些作用变化的受控因素。研究尚未取得实证结果。

## 三层研究与六项交付

| 材料 | 内容 |
|---|---|
| [研究任务书](docs/RESEARCH_BRIEF.md) | 问题、数据、方法、指标、三项待检验问题与风险 |
| [三层分析计划](docs/ANALYSIS_PLAN.md) | 性能、几何、工业语义的定义、对照和证据边界 |
| [核心相关工作](docs/RELATED_WORK.md) / [整理与访问状态](docs/LITERATURE_ACCESS.md) | 核心 12 篇；总台账 19 条均已基础整理，阅读深度逐条说明 |
| [资源核验](docs/RESOURCES.md) | 原始数据、位置/形态/来源与采集信息缺项 |
| [六项验收](docs/DELIVERABLES.md) | 本版材料、实现范围及未完成依赖 |

本仓库是可核验的科研起步骨架。已实现文件审计、环境探测、分组划分与方案检查；尚未实现或运行模型训练。工业数据原始目录由研究者后续提供。资料记载数量不能替代磁盘审计结果。

## Setup

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-audit.txt
python -m pip install -e . --no-deps
python -m unittest discover -s tests -v
python -m weldstudy.environment --out reports/environment.local.json
```

图像审计（保留原始文件，不作转换）：

```sh
python -m weldstudy.audit --root /actual/dataset/root --out reports/audit
python -m weldstudy.split --manifest reports/audit/manifest.csv --groups /actual/group_mapping.csv --out data/splits
```

`/actual/...` 是命令示例，不是已确认的数据路径。无分组证据时划分工具会拒绝执行。审计当前支持 Pillow 可读取的 PNG/JPEG/TIFF/BMP；DICOM 等列为不支持项，禁止默默丢弃。标注文件仅登记候选路径，不猜测标签格式或正常类别。原始位深与灰度转换规则待真实样本核验。

## Experiment contract

详见 `docs/protocol.md`。主比较：ResNet18 + SimCLR 与增加单个 CBAM 空间分支的模型；10%/50%/100% 嵌套训练组、配对随机种子、固定优化步数与校准池。主效应是各规模 ARI 配对差的预定等权平均，同时逐规模完整报告；规模交互为次要比较。

数据审计后先冻结独立的预实验协议，再开展数据相关预实验；合成 MPS 测试可先行。最终参数与三层分析计划在预实验后冻结，测试图像不参与拟合或参数选择。当前配置为 0.2-draft；检查器只针对最终训练门槛，应返回非零。训练与几何/语义分析代码均未实现。

## Paper

```sh
cd paper
latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex
```

使用 TeX Live 的 Latin Modern 与 Fandol 字体；缺失时安装相应 TeX 字体包。`references.bib` 与 `docs/literature.json` 一一对应，共 19 条，其中核心比较采用 12 条。论文是含摘要、章节、图和结果占位的通用 article 骨架。位置/形态证据不足时收缩机制主张；没有编造结果。

## Publication status

远端为 https://github.com/JTR892/30- ，公开可见。仅同步通用工程、研究协议与公开文献台账。原始工业资料、本机环境详情和详细本地进度不上传。远端完成状态以实际提交为准。

v0.1 本地 DOCX/PDF/XLSX 和压缩包保留为历史快照，本次不声称全部重制。当前六项研究约定以 v0.2 源码为准；提交版本以 Git 历史为准。

