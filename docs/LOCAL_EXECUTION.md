# 本地执行手册 v0.4

本仓库是公开仓库。真实图像、数据集绝对路径、label map、数据清单、测试标签、检查点和训练日志都应留在本地。GitHub Actions不会访问用户电脑或本地数据。

## 1. 安装基础环境

    python -m venv .venv
    source .venv/bin/activate
    python -m pip install --upgrade pip
    make install

## 2. 确认数据目录层级与类别映射

当前src/weldstudy/audit.py使用图像相对路径的第一层目录名映射类别。因此DATA_ROOT必须直接包含两个类别文件夹，例如：
- DATA_ROOT/实际缺陷文件夹/图像文件
- DATA_ROOT/实际无缺陷文件夹/图像文件

如果真实目录结构不同，先检查目录并修改/测试审计代码；不要为了适配脚本而移动或重命名原始数据。

复制config/label_map.example.json为config/label_map.local.json，将两个键替换为真实类别文件夹名称，值分别保持defect和no_defect。该文件已加入.gitignore。

## 3. 执行真实数据审计

    make audit DATA_ROOT="/你的二分类数据集根目录"

输出位于reports/audit/，包含manifest.csv和audit.json。核对实际文件数、可读数、类别映射、尺寸、模式、完全重复和冲突标签。审计脚本只读原始图像，不会修改或移动原始数据。

## 4. 生成图像级划分

确认审计无未解决的不可读图像、未映射标签和冲突重复后：

    make split

输出位于data/splits/。训练/聚类拟合/测试清单不含类别标签；测试标签另存为test_labels.locked.csv。文件权限不是加密，必须避免在训练和调参期间打开测试标签。

注意：10/50/100%训练子集比例以train划分为分母；不是全体数据的比例。

## 5. 运行自动化测试

    make test

GitHub Actions也会在push、pull request和手动触发时运行相同测试。测试使用临时合成图像，不读取真实数据集。

## 6. 重新编译论文

    make paper

要求本机安装XeLaTeX、latexmk、xeCJK、TikZ和Fandol/Latin Modern字体。CI使用GitHub-hosted Ubuntu runner安装对应TeX Live组件，并把生成的main.pdf保存为workflow artifact，不将PDF自动提交到仓库。

## 7. M1 Max环境检查与MPS smoke

    python -m pip install -r requirements-mps.txt
    make environment
    make mps-smoke

environment.json记录Python、macOS、芯片、内存和PyTorch/MPS是否可用。mps_smoke.json使用随机合成图像和普通torchvision ResNet18做短暂前反向传播。它只验证基本MPS执行能力，不是SimCLR双视图+空间注意力的吞吐结果，也不能替代真实图像Pilot。

## 8. 正式训练当前尚未开放

仓库目前没有完整的SimCLR/Attention训练器、成对实验调度器和聚类评估流水线。正式训练必须等训练代码实现、真实数据审计、使用权限确认、MPS smoke通过、真实图像Pilot通过、训练参数与分析计划冻结后再开始。详见docs/TRAINING_IMPLEMENTATION_PLAN.md。

## 9. 上传前检查

    git status --short

不要强制添加被忽略的文件。公开仓库不得包含真实图像、绝对路径、label map、manifest、测试标签、模型权重或本地运行日志。
