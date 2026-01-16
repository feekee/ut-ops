"""
SSH 操作 API
提供远程服务器连接和命令执行功能
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, field_validator
from typing import Optional, List
import asyncio
from datetime import datetime
from loguru import logger
import re

from app.config import settings
from app.services.ssh_service import SSHService, SSHConnectionError, CommandExecutionError

router = APIRouter()


class SSHConnectionRequest(BaseModel):
    """SSH 连接请求"""
    host: str
    port: int = 22
    username: str = "root"
    password: Optional[str] = None
    
    @field_validator('host')
    @classmethod
    def validate_host(cls, v):
        """验证主机地址"""
        # 简单的 IP 验证
        ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        hostname_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'
        
        if not (re.match(ip_pattern, v) or re.match(hostname_pattern, v)):
            raise ValueError('无效的主机地址')
        
        # 检查 IP 白名单
        if settings.SSH_ALLOWED_IPS and v not in settings.SSH_ALLOWED_IPS:
            raise ValueError(f'主机 {v} 不在允许列表中')
        
        return v


class CommandRequest(BaseModel):
    """命令执行请求"""
    host: str
    command: str
    port: int = 22
    username: str = "root"
    password: Optional[str] = None
    timeout: int = 30
    
    @field_validator('command')
    @classmethod
    def validate_command(cls, v):
        """验证命令是否在白名单中"""
        command_lower = v.lower().strip()
        
        # 检查命令是否在白名单中
        is_allowed = any(
            command_lower.startswith(allowed.lower()) 
            for allowed in settings.ALLOWED_COMMANDS
        )
        
        if not is_allowed:
            raise ValueError(f'命令不在允许列表中: {v}')
        
        # 检查危险字符
        dangerous_chars = [';', '&&', '||', '|', '`', '$(',  '>', '<', 'rm -rf', 'mkfs', 'dd if=']
        for char in dangerous_chars:
            if char in v:
                raise ValueError(f'命令包含不允许的字符: {char}')
        
        return v


class SSHTestResponse(BaseModel):
    """SSH 连接测试响应"""
    success: bool
    message: str
    host: str
    latency_ms: Optional[float] = None


class CommandResponse(BaseModel):
    """命令执行响应"""
    success: bool
    command: str
    stdout: str
    stderr: str
    exit_code: int
    execution_time_ms: float
    timestamp: str


class ServerStatusResponse(BaseModel):
    """服务器状态响应"""
    host: str
    online: bool
    cpu_usage: Optional[str] = None
    memory_usage: Optional[str] = None
    disk_usage: Optional[str] = None
    load_average: Optional[str] = None
    uptime: Optional[str] = None


@router.post("/test-connection", response_model=SSHTestResponse)
async def test_ssh_connection(request: SSHConnectionRequest):
    """测试 SSH 连接"""
    ssh_service = SSHService()
    
    try:
        start_time = datetime.now()
        password = request.password or settings.SSH_DEFAULT_PASSWORD
        
        success = await asyncio.to_thread(
            ssh_service.test_connection,
            host=request.host,
            port=request.port,
            username=request.username,
            password=password,
        )
        
        latency = (datetime.now() - start_time).total_seconds() * 1000
        
        return SSHTestResponse(
            success=success,
            message="连接成功" if success else "连接失败",
            host=request.host,
            latency_ms=latency,
        )
        
    except SSHConnectionError as e:
        return SSHTestResponse(
            success=False,
            message=str(e),
            host=request.host,
        )
    except Exception as e:
        logger.exception(f"SSH 连接测试失败: {request.host}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute", response_model=CommandResponse)
async def execute_command(request: CommandRequest):
    """
    执行远程命令
    
    ⚠️ 安全提醒：
    - 命令需要在白名单中
    - 禁止危险操作字符
    - 所有操作会被记录审计日志
    """
    ssh_service = SSHService()
    
    try:
        password = request.password or settings.SSH_DEFAULT_PASSWORD
        start_time = datetime.now()
        
        result = await asyncio.to_thread(
            ssh_service.execute_command,
            host=request.host,
            port=request.port,
            username=request.username,
            password=password,
            command=request.command,
            timeout=request.timeout,
        )
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # 记录审计日志
        logger.info(
            f"SSH Command Executed | Host: {request.host} | "
            f"User: {request.username} | Command: {request.command} | "
            f"Exit Code: {result['exit_code']}"
        )
        
        return CommandResponse(
            success=result['exit_code'] == 0,
            command=request.command,
            stdout=result['stdout'],
            stderr=result['stderr'],
            exit_code=result['exit_code'],
            execution_time_ms=execution_time,
            timestamp=datetime.now().isoformat(),
        )
        
    except CommandExecutionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except SSHConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.exception(f"命令执行失败: {request.command}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/server-status", response_model=ServerStatusResponse)
async def get_server_status(request: SSHConnectionRequest):
    """获取服务器状态摘要"""
    ssh_service = SSHService()
    
    try:
        password = request.password or settings.SSH_DEFAULT_PASSWORD
        
        status = await asyncio.to_thread(
            ssh_service.get_server_status,
            host=request.host,
            port=request.port,
            username=request.username,
            password=password,
        )
        
        return ServerStatusResponse(
            host=request.host,
            online=True,
            **status
        )
        
    except SSHConnectionError:
        return ServerStatusResponse(
            host=request.host,
            online=False,
        )
    except Exception as e:
        logger.exception(f"获取服务器状态失败: {request.host}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/diagnose")
async def diagnose_service(
    host: str,
    service_name: str,
    port: int = 22,
    username: str = "root",
    password: Optional[str] = None,
):
    """
    诊断指定服务状态
    
    执行一系列诊断命令检查服务健康状况
    """
    ssh_service = SSHService()
    password = password or settings.SSH_DEFAULT_PASSWORD
    
    diagnose_commands = {
        "service_status": f"systemctl status {service_name} --no-pager",
        "recent_logs": f"journalctl -u {service_name} -n 50 --no-pager",
        "process_check": f"ps aux | grep {service_name}",
    }
    
    results = {}
    
    try:
        for check_name, command in diagnose_commands.items():
            try:
                result = await asyncio.to_thread(
                    ssh_service.execute_command,
                    host=host,
                    port=port,
                    username=username,
                    password=password,
                    command=command,
                    timeout=30,
                )
                results[check_name] = {
                    "success": result['exit_code'] == 0,
                    "output": result['stdout'] or result['stderr'],
                }
            except Exception as e:
                results[check_name] = {
                    "success": False,
                    "output": str(e),
                }
        
        return {
            "host": host,
            "service": service_name,
            "timestamp": datetime.now().isoformat(),
            "diagnostics": results,
        }
        
    except Exception as e:
        logger.exception(f"服务诊断失败: {service_name}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/allowed-commands")
async def get_allowed_commands():
    """获取允许的命令列表"""
    return {
        "commands": settings.ALLOWED_COMMANDS,
        "note": "仅允许以这些前缀开头的命令"
    }
