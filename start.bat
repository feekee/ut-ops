@echo off
REM ============================================
REM 智能运维助手 - 启动脚本 (Windows)
REM 仅启动预构建的镜像，不进行构建
REM ============================================

setlocal enabledelayedexpansion

echo.
echo ============================================
echo  智能运维助手 - 启动工具
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

REM 检查 .env 文件
if exist .env (
    echo [✓] 已加载 .env 配置文件
) else (
    echo [!] 未找到 .env 文件
    echo 建议: copy env.example .env
    echo.
)

REM 检查镜像是否存在
echo [*] 检查镜像...
docker images | findstr "ops-assistant-frontend" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [X] 前端镜像不存在
    echo 请先运行: docker load -i frontend.tar
    echo.
    pause
    exit /b 1
)
echo [✓] 前端镜像已加载

docker images | findstr "ops-assistant-backend" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [X] 后端镜像不存在
    echo 请先运行: docker load -i backend.tar
    echo.
    pause
    exit /b 1
)
echo [✓] 后端镜像已加载

REM 启动服务
echo.
echo [*] 启动服务...
docker-compose up -d

if %ERRORLEVEL% NEQ 0 (
    echo [X] 启动失败
    docker-compose logs
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================
echo [✓] 启动成功！
echo ============================================
echo.
echo 服务地址：
echo   • 前端: http://localhost:3000
echo   • 后端: http://localhost:8000
echo   • API 文档: http://localhost:8000/docs
echo.
echo 查看日志：
echo   docker-compose logs -f
echo.
echo 停止服务：
echo   docker-compose down
echo.
pause
