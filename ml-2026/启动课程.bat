@echo off
rem 双击启动课程材料（Windows）：打开课件入口 + 启动 JupyterLab
cd /d "%~dp0"
start "" index.html
where jupyter >nul 2>nul
if %errorlevel%==0 (
  echo JupyterLab starting... close this window to stop it.
  jupyter lab --port 8888 --no-browser --ServerApp.token= --ServerApp.password=
) else (
  echo jupyter not found. Install with: pip install jupyterlab
  echo Course index opened in browser.
)
