# 环境与运行

华东师范大学数据科学与工程学院 · 本科三年级 · 机器学习部分（2026 秋）

## 一键启动

- **Windows**：双击 `启动课程.bat`
- **macOS**：双击 `启动课程.command`
- **终端**：在课程目录运行 `./start.sh`

请先进入本目录 `ml-2026`，再打开 [index.html](index.html) 并启动 JupyterLab（端口 8888）。**保持启动窗口开启**；关闭启动窗口后 JupyterLab 会一并退出。结束使用时可在终端按 Ctrl+C 关闭服务器。

## 首次使用：安装环境（约 10 分钟，只需一次）

「一键启动」假定环境已就绪。第一次使用请先完成以下三步；需要 Python 3.12 及以上（课堂数字基于 Python 3.14.6 + scikit-learn 1.9.0）。

**第 1 步 · 确认 Python**

```bash
python3 --version        # Windows 在 PowerShell 中执行: python --version
```

低于 3.12 时先到 [python.org](https://www.python.org/downloads/) 安装（Windows 安装时勾选 **Add python.exe to PATH**）。

**第 2 步 · 创建虚拟环境并安装依赖**

在本目录 `ml-2026` 内执行：

macOS / Linux：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install jupyterlab
```

Windows（PowerShell）：

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install jupyterlab
```

**第 3 步 · 注册课程内核（一次性）**

```bash
python -m ipykernel install --user --name ecnu-ml --display-name "机器学习课程 Python 3.14"
```

完成后 JupyterLab 的内核列表里才会出现 `ecnu-ml`。第 10 章的 `ecnu-hf` 内核在开放第 10 章时再按当时说明安装。

装好后回到「一键启动」。环境自检顺序：Python ≥ 3.12 → 提示符前是否出现 `(.venv)` → 是否在 `ml-2026` 目录内执行。完全不想装环境时，可将对应 `.ipynb` 上传 [Google Colab](https://colab.research.google.com/) 运行（第 10 章需要 GPU，Colab 免费版可用）。

## 课程材料在哪里

每章材料在 `lessons/0X-讲名/`：

| 文件 | 用途 |
|---|---|
| `slides.html` | 课件（浏览器打开，方向键翻页；无教师备注） |
| `notebook/` | 实验 notebook（在 JupyterLab 中交互运行） |
| `notebook.html` | 含已执行输出的阅读版（无需运行即可对照） |

入口页 [index.html](index.html) 汇总各章链接。

**学生参考外链**：[机器学习课程参考外链](docs/机器学习课程参考外链.md) 按章节整理了官方教程、数据集、其他学校课件和补充阅读，用于课前预习、课后复习和实验查阅；另有[延伸阅读与参考资源](docs/resources.html)按主题精简版。

## 内核选择（重要）

课件数字锚定在两组环境，**请按章节选择内核**：

| 内核名 | 用于 |
|---|---|
| **ecnu-ml**（`.venv`，scikit-learn 1.9.0） | 第 1–9 章 |
| **ecnu-hf**（`.venv-hf`，PyTorch + transformers） | 第 10 章 |

在 JupyterLab 菜单 **Kernel → Change Kernel** 切换。第 1–9 章请勿选 HF 内核，否则结果可能与课件不一致。建议 **File → Save Notebook As** 另存副本再改代码，避免覆盖原文件。两个内核都需先注册：`ecnu-ml` 见下方「首次使用：安装环境」第 3 步；`ecnu-hf` 在第 10 章开放时提供安装说明。

## 在 Lab 里操作

- **Shift+Enter**：运行当前单元格
- **Kernel → Restart Kernel and Run All Cells**：从头完整复现（耗时较长）

JupyterLab 默认只在本机访问（127.0.0.1），无需把 notebook 上传到公网。

## 换电脑或环境报错

虚拟环境绑定本机 Python，**不要**直接复制 `.venv` 或 `.venv-hf` 到其他电脑。请按「首次使用：安装环境」的三步在本机重新创建环境；仍失败时对照课件中的 Python / scikit-learn 版本说明。

## 离线阅读

`slides.html` 与 `notebook.html` 可直接用浏览器打开，无需联网。首次运行某些实验可能需要下载数据或模型，以各章 notebook 说明为准。
