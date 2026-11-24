# 验证记录 v0.3 · 2026-11-24

本次源码更新已提交至 GitHub。当前会话未取得本地15,194张原始图像，故不声称完成真实数据验证。

| 项目 | 状态 | 说明 |
|---|---|---|
| 合成审计/划分测试 | 已更新，需在本地执行 | 仅验证目录映射、SHA256去重、冲突拒绝、图像级分层、嵌套子集与标签隔离 |
| DRAFT协议门槛 | 应拒绝正式训练，需本地执行 | 不代表模型已就绪 |
| 真实数据审计 | 未执行 | 数量、可读性、类别、重复未知 |
| MPS smoke test | 未执行 | 吞吐与峰值内存未知 |
| 模型训练/分析 | 未实现/未执行 | 无性能结果 |
| LaTeX编译 | 本次未编译 | 需本地运行 latexmk 并检查PDF |

本地运行：
```sh
python -m unittest discover -s tests -v
python -m weldstudy.protocol --config config/protocol.json
cd paper && latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex
```
DRAFT协议检查返回非零为预期。真实数据、许可、MPS、测试标签锁定和参数冻结前，不得将协议改为 FROZEN。
