@echo off
chcp 65001 >nul
echo ================================================
echo     魔A量化交易系统 - 便携版
echo ================================================
echo.

cd /d "."

echo 正在启动系统（开发模式）...
echo.

REM 启动后端服务
start "魔A量化交易系统-后端" cmd /k "cd server && python app.py"

REM 等待后端启动
timeout /t 3 /nobreak >nul

REM 启动前端开发服务器
start "魔A量化交易系统-前端" cmd /k "npm run dev"

echo.
echo 系统已启动！
echo 后端地址: http://localhost:3001
echo 前端地址: http://localhost:5173
echo.
echo 按任意键退出...
pause >nul
