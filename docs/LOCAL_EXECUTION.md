# 本地审计执行说明 · v0.5 · 2026-11-27

原始图像/XML始终只读，详细产物均保存在Git忽略的reports/audit/。真实路径只写config/paths.local.json；按实际目录填写config/xml_audit.local.json，结构见xml_audit.example.json。

```sh
python -m pip install -e .
python -m unittest discover -s tests -v
python -m weldstudy.xml_audit --root /actual/data/root \
  --config config/xml_audit.local.json --out reports/audit/NEW_EMPTY_VERSION
python scripts/verify_xml_audit.py --root /actual/data/root --audit reports/audit/NEW_EMPTY_VERSION
# 可选：有限文件名候选平移重叠诊断，不证明已经排除所有近重复/同源
python scripts/check_content_overlap.py --root /actual/data/root --audit reports/audit/NEW_EMPTY_VERSION
python -m weldstudy.protocol --config config/protocol.json
```

最后一项在当前DRAFT下必须返回2。`make split`与旧split CLI已停用；旧binary辅助函数仅保留历史合成测试。没有经过v0.5数据资格与冻结，不可用旧脚本生成正式分区。

outputs：images.csv/jsonl逐图、objects.csv逐对象、xml_records.jsonl逐XML、dimensions.csv全尺寸、review_queue.csv全量待专业语义复核、duplicates报告，以及independent_verification.json复算。输出目录非空时全量审计拒绝覆盖，以保留历史。

## 合并去重复核任务

在完整审计后，以同一真实数据根目录构建新的私有任务版本：

```sh
python -m weldstudy.review_tasks --root /actual/data/root \
  --audit reports/audit/AUDIT_VERSION --out reports/audit/NEW_TASK_VERSION
python scripts/verify_review_tasks.py --root /actual/data/root \
  --audit reports/audit/AUDIT_VERSION --package reports/audit/NEW_TASK_VERSION
python scripts/render_review_tasks.py --package reports/audit/NEW_TASK_VERSION
```

独立验证重新读全部原图/XML并核对CSV，失败返回2。HTML与JPEG只供定位，原始TIFF链接保留；专业复核在原图上进行，结论另存版本。构建程序拒绝覆盖已有非空输出。完整任务范围、合并规则和本次统计见[交付汇总](REVIEW_TASK_PACKAGE_2026-11-27.md)。

## 类别与规则草案的私有问题关联

```sh
python -m weldstudy.annotation_draft --audit reports/audit/AUDIT_VERSION \
  --package reports/audit/TASK_VERSION --out reports/audit/NEW_DRAFT_VERSION
```

默认读取`config/taxonomy.draft.json`与`config/annotation_questions.draft.json`。输出全量逐图问题范围、与既有任务的关联、原标签统计和空白人工填报表；选择器仅表示复核范围，不生成诊断、排除、训练子集或K。既有审计、任务包和原始目录作为只读输入，输出必须为独立新目录。专家定义、适用标准和实际确认字段保留待填。

47张不同图像的本地AI抽查已经完成；专业缺陷分类仍待标注人员依据规范复核。图库生成脚本只读取已固定的visual/selection.json，需提供本地CJK字体；图库不上传GitHub。

真实模型训练、正式划分与几何分析尚未完成。MPS合成smoke不能替代真实SimCLR双视图/Attention的吞吐与内存测量。详见[计划](ONE_MONTH_MANUSCRIPT_PLAN.md)。
