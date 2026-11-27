# 标注草案的术语资料与适用性登记 · 2026-11-27

本次新增8条技术资料记录，机器台账为[annotation_sources.json](annotation_sources.json)。它们与原L01–L19论文台账分开编号；未访问L06和L13–L17，未提升既有论文阅读深度。下表区分已整理、实际访问及阅读范围。

| 编号与官方/机构原始来源 | 实际访问与阅读范围 | 本草案中的用途 |
|---|---|---|
| A01 [ISO 6520-1:2007](https://www.iso.org/standard/40229.html) | 官方目录、状态与摘要；未取得标准全文 | 了解几何不完美分类资料的范围，向提供者核对实际命名依据 |
| A02 [ISO 10675-1:2021](https://www.iso.org/standard/79616.html) | 官方目录、版本与摘要；未取得标准全文 | 了解公开的射线验收范围，询问实际适用材料、接头和检测要求 |
| A03 [TWI：Porosity](https://www.twi-global.com/technical-knowledge/job-knowledge/defects-imperfections-in-welds-porosity-042) | 官网HTML已打开，核对Identification相关段落 | 气体孔穴概念提纲 |
| A04 [TWI：Sidewall and inter-run fusion](https://www.twi-global.com/technical-knowledge/job-knowledge/weld-defects-imperfections-in-welds-lack-of-sidewall-and-inter-run-fusion-041) | 官网HTML已打开，核对Identification相关段落 | 侧壁与层间未熔合概念提纲 |
| A05 [TWI：Incomplete root fusion or penetration](https://www.twi-global.com/technical-knowledge/job-knowledge/weld-defects-imperfections-incomplete-root-fusion-or-penetration-040) | 官网HTML已打开，核对Identification相关段落 | 根部相关标签的边界问题 |
| A06 [TWI：Shape imperfections, Part 1](https://www.twi-global.com/technical-knowledge/job-knowledge/a-general-review-of-geometric-shape-imperfections-types-and-causes-part-1-067) | 官网文本的搜索提取已读，直开超时；没有称全文访问 | 咬边/overlap及几何外形概念；中文标签映射待确认 |
| A07 [TWI：Shape imperfections, Part 2](https://www.twi-global.com/technical-knowledge/job-knowledge/a-general-review-of-the-causes-and-acceptance-of-shape-imperfections-part-2-068?vAction=swpTextOnly) | 官网HTML已打开，核对Root concavity相关段落 | 内凹的候选概念核对 |
| A08 [TWI：Hot/solidification cracking](https://www.twi-global.com/technical-knowledge/faqs/faq-what-is-hot-cracking-solidification-cracking) | 官网HTML已打开，核对开头相关段落 | 具体裂纹子型示例，不将全部裂纹限定为此机制 |

ISO 6520-1公开摘要将其定位为熔焊几何不完美的分类与描述资料；ISO 10675-1公开摘要说明了特定材料和接头的射线验收范围。二者用途有别，不能由分类名称推出验收结果。提供者尚未确认本数据适用的标准、工艺或等级，因此`applied_standard`保持null，不填条款编号、ISO分类编号或验收数值。[ISO分类目录](https://www.iso.org/standard/40229.html)、[ISO验收目录](https://www.iso.org/standard/79616.html)。

TWI资料作为概念核对材料，未作为本数据验收规范；网页中的工艺原因、数值示例和其它标准要求不迁入本项目规则。没有转载标准正文、机构配图或原图示例。当前论文未采用这些规范性结论，故未将它们写成稿件中已使用的检测标准；本次同步范围为草案、专门资料台账及对应比较表。
