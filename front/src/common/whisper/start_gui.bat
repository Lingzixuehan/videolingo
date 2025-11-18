@echo off
REM Whisper GUI 启动脚本 (Windows)
REM 双击运行即可启动 GUI

cd /d "%~dp0"

echo.
echo ================================================
echo   Whisper GUI 启动
echo ================================================
echo.
echo 正在启动图形化界面...
echo.

python gui/whisper.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ================================================
    echo   启动失败！请检查错误信息
    echo ================================================
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================
echo   GUI 应用已关闭
echo ================================================
echo.
pause
