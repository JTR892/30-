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

47张不同图像的本地AI抽查已经完成；专业缺陷分类仍待标注人员依据规范复核。图库生成脚本只读取已固定的visual/selection.json，需提供本地CJK字体；图库不上传GitHub。

真实模型训练、正式划分与几何分析尚未完成。MPS合成smoke不能替代真实SimCLR双视图/Attention的吞吐与内存测量。详见[计划](ONE_MONTH_MANUSCRIPT_PLAN.md)。
