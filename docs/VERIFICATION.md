# 当前验证入口 · 2026-11-27

全量审计阶段23项合成测试、DRAFT/旧split关闭、实际审计与独立复算、论文构建见[审查与验证](CODE_REVIEW_2026-11-27.md)。随后任务包新增6项测试，本地共29项通过；四轮剩余集合和逐文件/CSV复核见[任务包汇总](REVIEW_TASK_PACKAGE_2026-11-27.md)。下方保留先前版本历史记录，不代表本次远端CI状态。

# 验证记录 v0.3 · 2026-11-24

## GitHub 云端 CI：已通过

最新工作流：`.github/workflows/ci.yml`

- 运行编号：#2
- Commit：`3a152cb59299ac42ca844d72b7ad57ca86ba1ee8`
- 运行结果：`success`
- 运行链接：https://github.com/JTR892/30-/actions/runs/45390330753

| 检查项 | 结果 |
|---|---|
| Python 3.10 合成测试 + DRAFT 门槛 | PASS |
| Python 3.11 合成测试 + DRAFT 门槛 | PASS |
| Python 3.12 合成测试 + DRAFT 门槛 | PASS |
| Python 3.13 合成测试 + DRAFT 门槛 | PASS |
| XeLaTeX 论文编译 | PASS |
| PDF artifact 上传 | PASS |

测试覆盖目录标签映射、图像级划分、嵌套训练子集、标签隔离、完全重复冲突拒绝和协议冻结门槛。DRAFT协议返回非零是预期行为，说明正式训练被正确拦截。

编译产物：`manuscript-pdf`，约 164 KB。Artifact 保留至 2026-12-08 12:08 UTC，可从上述 Actions 运行页面下载。PDF 由 CI 构建，没有自动提交到仓库。

## 必须在本地完成的验证

| 项目 | 状态 | 验证方式 |
|---|---|---|
| 真实数据审计 | 未执行 | `make audit DATA_ROOT="/实际数据路径"` |
| 数据划分 | 未执行 | `make split`；检查数量、比例、标签隔离和报告 |
| M1 Max MPS 环境 | 未执行 | `make environment` |
| 合成数据 MPS 冒烟测试 | 脚本已加入，未在 M1 Max 执行 | 安装 `requirements-mps.txt` 后运行 `make mps-smoke` |
| SimCLR/Attention 正式训练 | 尚未实现 | 训练器与参数冻结前不得启动 |
| 真实实验分析 | 未执行 | 训练与聚类代码完成后执行 |

真实数据、路径、label map、split manifests、测试标签、检查点和训练日志不得上传公开 GitHub。CI 不读取这些本地文件，也不访问用户的 M1 Max。

## 本地命令

```sh
make install
make test
make paper
make audit DATA_ROOT="/实际数据路径"
make split
python -m pip install -r requirements-mps.txt
make environment
make mps-smoke
```

DRAFT协议检查返回非零为预期。真实数据、许可、MPS、测试标签锁定和参数冻结前，不得将协议改为 FROZEN。
