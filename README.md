# 30- · 小论文

Weld radiograph attention study

研究问题：在固定优化步数和固定聚类校准池条件下，目标域无标签训练数据规模是否改变空间注意力对整幅焊缝 X 射线图像聚类的收益？

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

详见 `docs/protocol.md`。主比较：ResNet18 + SimCLR 与增加单个 CBAM 空间分支的模型；10%/50%/100% 嵌套训练组、配对随机种子；固定优化步数。所有正式参数在预实验后冻结。`config/protocol.json` 仍为 DRAFT，检查器返回非零是预期行为，不能绕过后宣称正式实验已启动。

## Paper

```sh
cd paper
latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex
```

使用 TeX Live 的 Latin Modern 与 Fandol 字体；缺失时安装相应 TeX 字体包。`references.bib` 与 `docs/literature.json` 一一对应。论文是含摘要、章节、图和结果占位的骨架；没有编造结果。

## Publication status

远端为 https://github.com/JTR892/30- ，公开可见。仅同步通用工程、研究协议与公开文献台账。原始工业资料、本机环境详情和详细本地进度不上传。远端完成状态以实际提交为准。

