# 验证记录 v0.3 · 2026-11-24

## GitHub 云端 CI
工作流：`.github/workflows/ci.yml`。每次 push 到 main、面向 main 的 pull request 或手动触发时运行。
- Python 3.10/3.11/3.12/3.13 合成测试；
- 确认当前 DRAFT 协议会阻止正式训练；
- XeLaTeX 编译 `paper/main.tex`，成功后上传 PDF artifact。

本次提交后首次运行结果尚待 GitHub Actions 完成；不得在结果返回前标记为通过。运行链接：`https://github.com/JTR892/30-/actions`。

## 必须在本地完成的验证
| 项目 | 状态 | 验证方式 |
|---|---|---|
| 真实数据审计 | 未执行 | `make audit DATA_ROOT="/实际数据路径"` |
| 数据划分 | 未执行 | `make split`；检查数量、比例、标签隔离和报告 |
| M1 Max MPS 环境 | 未执行 | `make environment` |
| 合成数据 MPS 冒烟测试 | 脚本已加入，未执行 | 安装 `requirements-mps.txt` 后运行 `make mps-smoke` |
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
