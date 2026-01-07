@echo off
:: Quick launcher for Create-AIPackage.ps1
:: Double-click this file or run from command prompt
::
:: Usage:
::   ai-package.bat          - Creates lite package (default, ~30KB)
::   ai-package.bat standard - Creates standard package (~50KB)

setlocal

set MODE=%1
if "%MODE%"=="" set MODE=lite

echo.
echo ========================================
echo   Digital Watercolors AI Package Creator
echo   Mode: %MODE%
echo ========================================
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0tools\Create-AIPackage.ps1" -Mode %MODE%

echo.
pause
