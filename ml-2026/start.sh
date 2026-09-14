#!/usr/bin/env bash
cd "$(dirname "$0")"
( open index.html 2>/dev/null || xdg-open index.html ) &
if command -v jupyter >/dev/null; then
  echo "启动 JupyterLab（交互运行 notebook，Ctrl+C 退出）…"
  exec jupyter lab --port 8888
else
  echo "未安装 jupyter，交互运行请先: pip install jupyterlab"
  echo "课件已在本浏览器打开。"
fi
