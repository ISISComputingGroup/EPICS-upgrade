setlocal

cd /d %~dp0

call ..\..\..\config_env.bat

set PYTHONUNBUFFERED=1

%PYTHON3% -u upgrade.py
