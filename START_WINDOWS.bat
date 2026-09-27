@echo off
cd /d "%~dp0"
py -3 -m hepatogenesis serve
if errorlevel 1 pause
