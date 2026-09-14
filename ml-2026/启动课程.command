#!/usr/bin/env bash
# 双击启动课程材料（.command 由 macOS 终端执行，中文路径可靠）
# 优先使用仓库自带虚拟环境 .venv（内含 jupyterlab）；关闭本终端窗口 = JupyterLab 一起退出
cd "$(dirname "$0")" 2>/dev/null || cd "/Users/momo/Documents/workspace/教学/2026机器学习与概率统计-本科" || exit 1
( open index.html 2>/dev/null ) &
JP="$PWD/.venv/bin/jupyter"
[ -x "$JP" ] || JP="$(command -v jupyter || true)"
if [ -n "$JP" ]; then
  echo "启动 JupyterLab（入口页的「交互运行」链接此时可点击；关闭本窗口即退出）…"
  exec "$JP" lab --port 8888 --no-browser --ServerApp.token= --ServerApp.password=
else
  echo "未找到 jupyter：请先创建环境  python3 -m venv .venv && .venv/bin/pip install jupyterlab scikit-learn matplotlib"
  echo "课件入口已在本浏览器打开。"
  exit 0
fi
