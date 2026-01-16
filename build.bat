@echo off
REM ============================================
REM 智能运维助手 - Docker 构建脚本 (Windows)
REM ============================================

setlocal enabledelayedexpansion

echo.
echo ============================================
echo  智能运维助手 - Docker 构建工具
echo ============================================
echo.

REM 参数检查
set CLEAN_BUILD=%1
if "%CLEAN_BUILD%"=="" set CLEAN_BUILD=normal

if "%CLEAN_BUILD%"=="clean" (
    echo [*] 清理 Docker 缓存...
    docker system prune -af
    docker volume prune -f
    echo [✓] 缓存清理完成
    echo.
)

REM 检查 .env 文件
if exist .env (
    echo [✓] 已找到 .env 文件
) else (
    echo [!] 未找到 .env 文件，使用默认配置
    echo 建议: copy env.example .env
    echo.
)

REM 构建前端
echo.
echo [*] 构建前端镜像...
docker-compose build frontend
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [X] 前端镜像构建失败
    echo.
    echo 故障排查：
    echo   1. 检查网络连接
    echo   2. 查看文件: docs\npm-troubleshooting.md
    echo   3. 尝试命令: docker-compose build --no-cache frontend
    echo.
    pause
    exit /b 1
)
echo [✓] 前端镜像构建成功

REM 构建后端
echo.
echo [*] 构建后端镜像...
docker-compose build backend
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [X] 后端镜像构建失败
    echo.
    echo 故障排查：
    echo   查看构建日志: docker-compose build --no-cache backend
    echo.
    pause
    exit /b 1
)
echo [✓] 后端镜像构建成功

REM 显示镜像信息
echo.
echo [*] 镜像信息：
docker images | findstr "ops-assistant"

REM 完成
echo.
echo ============================================
echo [✓] 构建完成！
echo ============================================
echo.
echo 下一步：
echo   1. docker-compose up -d
echo   2. 访问 http://localhost:3000
echo   3. 查看日志: docker-compose logs -f
echo.
pause
