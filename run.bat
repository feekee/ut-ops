@echo off
REM ============================================
REM 智能运维助手 - 快速启动脚本
REM 使用已有的镜像直接启动服务
REM ============================================

setlocal enabledelayedexpansion

echo.
echo ============================================
echo  智能运维助手 - 启动服务
echo ============================================
echo.

REM 检查 Docker 是否运行
docker info >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [X] Docker 未运行或未安装
    echo 请先启动 Docker Desktop 或 Docker daemon
    echo.
    pause
    exit /b 1
)

echo [*] 启动服务中...
echo.

REM 启动服务
docker-compose -f docker-compose.prod.yml up -d

if %ERRORLEVEL% NEQ 0 (
    echo [X] 启动失败
    docker-compose -f docker-compose.prod.yml logs
    echo.
    pause
    exit /b 1
)

REM 等待服务启动
echo [*] 等待服务启动...
timeout /t 3 /nobreak >nul

REM 检查服务状态
docker-compose -f docker-compose.prod.yml ps

echo.
echo ============================================
echo [✓] 服务已启动！
echo ============================================
echo.
echo 访问地址：
echo   • 前端: http://localhost:3000
echo   • 后端: http://localhost:8000
echo   • API 文档: http://localhost:8000/docs
echo.
echo 常用命令：
echo   查看日志: docker-compose -f docker-compose.prod.yml logs -f
echo   停止服务: docker-compose -f docker-compose.prod.yml down
echo   重启服务: docker-compose -f docker-compose.prod.yml restart
echo.
pause
