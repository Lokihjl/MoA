@echo off
chcp 65001 >nul
echo ================================================
echo     魔A量化交易系统
echo ================================================
echo.

cd /d "."

echo 正在启动系统...
echo 请稍候，系统正在初始化...

if exist "dist\魔A量化交易系统.exe" (
    start "" "dist\魔A量化交易系统.exe"
    echo 系统已启动！
    echo.
    echo 系统访问地址: http://localhost:3001
    echo.
    echo 按任意键退出...
    pause >nul
) else (
    echo 错误：找不到可执行文件！
    echo 请确保打包过程已完成。
    echo.
    pause
)
