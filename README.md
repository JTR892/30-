# 焊缝X射线图像多类别聚类研究

工作题目：不同训练样本规模下空间注意力对焊缝X射线图像多类别无监督聚类的影响。

当前方向为v0.5：将无缺陷作为一个类别，同时区分经核验的缺陷类型；使用提供的焊缝区域图像；设置低、中、高无标签训练规模，具体数量待研究资格确认。候选模型为ResNet18 + SimCLR，对比有无空间分支，结构和参数尚未冻结。

## 2026-11-27实际进展

本次收到32,932张TIFF和13,859份XML。图像均完整解码，XML均解析且尺寸与对应图像一致。审计发现目录/XML类别冲突、多缺陷、重复标注冲突以及跨现成分区的完全重复。详细数字、候选定义和裁剪证据边界见[全量审计](docs/DATA_AUDIT_2026-11-27.md)及[机器汇总](docs/data_audit_summary.json)。

数据资格为 **HOLD**。47张不同图像完成AI视觉分诊，专业语义核验仍待完成。用户确认good代表合格，但目前没有原始底片和标注规范；不能把AI抽查当作全部图像的专业判读认证。尺寸不证明逐张裁剪史，像素去重数不等于独立焊口数。

本次为预分区审计，包含对现成train/val/test目录标签的访问；这些目录不构成尚未接触的最终测试集。正式测试、来源连通组与协议须后续冻结。没有模型训练或聚类实验结果。

第一步整理已将重复、类别、名称与坐标问题合并为[1,884个去重复核任务](docs/REVIEW_TASK_PACKAGE_2026-11-27.md)，覆盖2,140个原图文件，其余30,792张有完整剩余记录。原图/XML保留；任务包已完成四轮剩余集合独立复算，专业类别裁决与数据资格仍待完成。

## 审计与代码状态

已实现：

- 逐图完整解码、16位/通道/帧数与尺寸登记；
- 同目录同主名XML解析、filename/尺寸/对象类别/坐标包络检查；
- 文件字节与未经归一化的像素SHA256，重复、标注集合和跨分区冲突检查；
- 保留多标签及未知状态，生成全量私有问题队列；
- 独立字节重哈希与XML复算；有限文件名候选的逐像素重叠诊断。

主入口：

```sh
python -m pip install -e .
python -m unittest discover -s tests -v
# 先依据真实结构填写本地配置，输出使用新的空目录。
python -m weldstudy.xml_audit --root /actual/data/root \
  --config config/xml_audit.local.json --out reports/audit/NEW_VERSION
python scripts/verify_xml_audit.py --root /actual/data/root --audit reports/audit/NEW_VERSION
python -m weldstudy.protocol --config config/protocol.json
```

`/actual/...`为示例。本地配置结构见[示例](config/xml_audit.example.json)。审计读取原始数据，输出在原始目录之外；不修复框、不重标、不移动文件。

`config/protocol.json`已改为v0.5 DRAFT，数据资格与训练门槛均未通过，CLI应返回2。v0.4配置保留于[历史文件](config/protocol.legacy_v0.4.json)。旧`audit.py`/`split.py`是二分类历史代码；`make split`和旧split CLI已停用，旧辅助函数只保留合成回归检查。新审计输出不能作为正式划分放行依据。

尚未实现或完成：专业语义认证、全部近重复/来源追溯、v0.5正式划分流程、SimCLR/Attention训练器、真实图像Pilot、冻结协议与正式聚类分析。行政门槛字段不替代实际证据审阅。

## 研究边界

- 类别标签不进入表征训练、主训练子集选择、模型选择或K-means拟合；外部监督预训练如使用须披露。
- 同一焊口、源图及重复连通组件不能跨分区；未知来源不冒称独立。
- 多缺陷图保留多标签，未知标签不当正常，`其它缺陷`待专业定义，焊缝标签暂按辅助区域登记。
- K值、类别、预算、主对比和统计方案待审计及训练侧Pilot后冻结；不沿用K=2作为多类别默认值。
- 测试不参与拟合、调参或checkpoint选择。热图与几何变化不单独证明因果机制，灰度不替代曝光记录。
- 保留零效应、负效应、失败和覆盖范围；不把合成测试、CI或数据审计写成模型实验成功。

## 文档和计划

[研究任务书](docs/RESEARCH_BRIEF.md) · [分析计划](docs/ANALYSIS_PLAN.md) · [当前状态](docs/STATUS.md) · [资源](docs/RESOURCES.md) · [代码审查](docs/CODE_REVIEW_2026-11-27.md) · [修订后进度计划](docs/ONE_MONTH_MANUSCRIPT_PLAN.md) · [变更记录](docs/PROTOCOL_CHANGELOG.md)

论文为未填模型结果的通用LaTeX骨架，并非官方期刊模板。编译：

```sh
cd paper
latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex
```

文献保持既有19条台账；阅读深度见[LITERATURE_ACCESS](docs/LITERATURE_ACCESS.md)。本次未更新文献或提升阅读深度。原始工业图像/XML、用户PDF、真实路径、逐图清单、审阅图、权重与训练产物不上传公开GitHub。公开内容为通用代码、协议与聚合审计结论。
