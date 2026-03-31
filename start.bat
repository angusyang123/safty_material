@echo off
echo ========================================
echo    库存预测分析系统 - 启动脚本
echo ========================================
echo.

echo [1/2] 启动后端服务...
start "Backend API" cmd /k "cd /d %~dp0backend && uvicorn app.main:app --reload --port 8000"
timeout /t 3 /nobreak > nul

echo [2/2] 启动前端服务...
start "Frontend Dev" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ========================================
echo 服务启动完成！
echo.
echo 后端 API: http://localhost:8000
echo API 文档: http://localhost:8000/docs
echo 前端页面: http://localhost:5173
echo ========================================
echo.
pause
