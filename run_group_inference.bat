@echo off
setlocal
cd /d "%~dp0"
python -m plots.group_inference.run %*
pause
