# 本地执行手册 v0.3

本仓库是公开仓库。真实图像、数据集绝对路径、label map、数据清单、测试标签、检查点和训练日志都应留在本地。GitHub Actions 不会访问用户电脑或本地数据。

## 1. 安装基础环境

建议在项目虚拟环境中执行：

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
make install
```

## 2. 配置本地类别目录映射

```sh
cp config/label_map.example.json config/label_map.local.json
```

编辑 `config/label_map.local.json`，将两个键替换成真实的类别文件夹名，值必须分别为 `defect` 和 `no_defect`。该文件已加入 `.gitignore`。

## 3. 执行真实数据审计

```sh
make audit DATA_ROOT="/你的二分类数据集根目录"
```

输出位于 `reports/audit/`，包含 `manifest.csv` 和 `audit.json`。核对实际文件数、可读数、类别映射、尺寸、完全重复和冲突标签。审计脚本只读原始图像，不会修改或移动原始数据。

## 4. 生成图像级划分

确认审计无未解决的不可读图像、未映射标签和冲突重复后：

```sh
make split
```

输出位于 `data/splits/`。训练/校准/测试清单不含类别标签；测试标签另存为 `test_labels.locked.csv`。文件权限不是加密，必须避免在训练和调参期间打开测试标签。

## 5. 运行自动化测试

```sh
make test
```

GitHub Actions 也会在 push、pull request 和手动触发时运行相同测试。测试使用临时合成图像，不读取真实数据集。

## 6. 重新编译论文

```sh
make paper
```

要求本机安装 XeLaTeX、latexmk、xeCJK、TikZ 和 Fandol/Latin Modern 字体。CI 使用 GitHub-hosted Ubuntu runner 安装对应 TeX Live 组件，并把生成的 `main.pdf` 保存为 workflow artifact，不将 PDF 自动提交到仓库。

## 7. M1 Max 环境检查与 MPS smoke

```sh
python -m pip install -r requirements-mps.txt
make environment
make mps-smoke
```

`environment.json` 记录 Python、macOS、芯片、内存和 PyTorch/MPS 是否可用。`mps_smoke.json` 使用随机合成图像和 torchvision ResNet18 做短暂前反向传播，记录吞吐与显存占用。它只验证 MPS 能否执行基本训练步骤，不是 SimCLR/Attention 的性能结果，也不能替代真实训练预算测试。

## 8. 正式训练当前尚未开放

仓库目前没有完整的 SimCLR/Attention 训练器、成对实验调度器和聚类评估流水线。正式训练必须等训练代码实现、真实数据审计、使用许可确认、MPS smoke 通过、训练参数与分析计划冻结后再开始。详见 `docs/TRAINING_IMPLEMENTATION_PLAN.md`。

## 9. 上传前检查

```sh
git status --short
```

不要强制添加被忽略的文件。公开仓库不得包含真实图像、绝对路径、label map、manifest、测试标签、模型权重或本地运行日志。
