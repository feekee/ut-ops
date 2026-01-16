"""
配置管理模块
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""
    
    # 基础配置
    APP_NAME: str = "智能运维助手"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Dify API 配置
    DIFY_API_BASE_URL: str = "http://localhost/v1"
    DIFY_API_KEY: str = ""
    DIFY_APP_ID: str = ""
    
    # SSH 配置
    SSH_DEFAULT_USERNAME: str = "root"
    SSH_DEFAULT_PASSWORD: str = ""
    SSH_DEFAULT_PORT: int = 22
    SSH_TIMEOUT: int = 30
    SSH_ALLOWED_IPS: List[str] = []  # IP 白名单，空表示不限制
    
    # 命令白名单
    ALLOWED_COMMANDS: List[str] = [
        # kubectl 命令
        "kubectl get",
        "kubectl describe",
        "kubectl logs",
        "kubectl top",
        # docker 命令
        "docker ps",
        "docker logs",
        "docker inspect",
        "docker stats",
        # 系统命令
        "systemctl status",
        "df -h",
        "free -m",
        "top -bn1",
        "ps aux",
        "netstat -tlnp",
        "ss -tlnp",
        "ping",
        "curl",
        "cat /var/log",
        "tail -f",
        "journalctl",
    ]
    
    # 数据库配置
    DATABASE_URL: str = "sqlite+aiosqlite:///./ops_assistant.db"
    
    # Redis 配置
    REDIS_URL: Optional[str] = None
    
    # JWT 配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # CORS 配置
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


settings = get_settings()
