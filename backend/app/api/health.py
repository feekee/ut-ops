"""
健康检查 API
"""
from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/ready")
async def readiness_check():
    """就绪检查接口"""
    return {
        "status": "ready",
        "timestamp": datetime.now().isoformat(),
    }
