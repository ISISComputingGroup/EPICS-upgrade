setlocal

call %~dp0..\..\..\config_env.bat

set PYTHONUNBUFFERED=1

C:\Instrument\Apps\Python3\python.exe -u upgrade.py
