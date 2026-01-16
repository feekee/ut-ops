"""
知识库 API
与 Dify 知识库功能交互
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, List
import httpx
from loguru import logger

from app.config import settings

router = APIRouter()


class DocumentInfo(BaseModel):
    """文档信息"""
    id: str
    name: str
    word_count: int
    hit_count: int
    status: str
    created_at: str


class KnowledgeBaseInfo(BaseModel):
    """知识库信息"""
    id: str
    name: str
    description: Optional[str]
    document_count: int
    word_count: int


@router.get("/datasets")
async def list_datasets():
    """获取知识库列表"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{settings.DIFY_API_BASE_URL}/datasets",
                headers={
                    "Authorization": f"Bearer {settings.DIFY_API_KEY}",
                },
                params={"page": 1, "limit": 20}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.text
                )
            
            return response.json()
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="请求超时")
    except Exception as e:
        logger.exception("获取知识库列表失败")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/datasets/{dataset_id}/documents")
async def list_documents(dataset_id: str, page: int = 1, limit: int = 20):
    """获取知识库中的文档列表"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{settings.DIFY_API_BASE_URL}/datasets/{dataset_id}/documents",
                headers={
                    "Authorization": f"Bearer {settings.DIFY_API_KEY}",
                },
                params={"page": page, "limit": limit}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.text
                )
            
            return response.json()
            
    except Exception as e:
        logger.exception("获取文档列表失败")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/datasets/{dataset_id}/documents/upload")
async def upload_document(
    dataset_id: str,
    file: UploadFile = File(...),
    indexing_technique: str = Form(default="high_quality"),
):
    """
    上传文档到知识库
    
    支持格式: PDF, DOCX, TXT, MD
    """
    allowed_types = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
        "text/markdown",
    ]
    
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: {file.content_type}"
        )
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            # 读取文件内容
            file_content = await file.read()
            
            # 构建 multipart 请求
            files = {
                "file": (file.filename, file_content, file.content_type)
            }
            
            data = {
                "indexing_technique": indexing_technique,
                "process_rule": {
                    "mode": "automatic"
                }
            }
            
            response = await client.post(
                f"{settings.DIFY_API_BASE_URL}/datasets/{dataset_id}/document/create_by_file",
                headers={
                    "Authorization": f"Bearer {settings.DIFY_API_KEY}",
                },
                files=files,
                data={"data": str(data)}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.text
                )
            
            return response.json()
            
    except Exception as e:
        logger.exception("上传文档失败")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/datasets/{dataset_id}/documents/{document_id}")
async def delete_document(dataset_id: str, document_id: str):
    """删除知识库中的文档"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.delete(
                f"{settings.DIFY_API_BASE_URL}/datasets/{dataset_id}/documents/{document_id}",
                headers={
                    "Authorization": f"Bearer {settings.DIFY_API_KEY}",
                },
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.text
                )
            
            return {"status": "deleted", "document_id": document_id}
            
    except Exception as e:
        logger.exception("删除文档失败")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/datasets/{dataset_id}/retrieve")
async def retrieve_from_knowledge(
    dataset_id: str,
    query: str,
    top_k: int = 5,
):
    """
    从知识库检索相关内容
    
    用于 RAG 场景的内容召回
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.DIFY_API_BASE_URL}/datasets/{dataset_id}/retrieve",
                headers={
                    "Authorization": f"Bearer {settings.DIFY_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "query": query,
                    "top_k": top_k,
                    "score_threshold": 0.5,
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.text
                )
            
            return response.json()
            
    except Exception as e:
        logger.exception("知识库检索失败")
        raise HTTPException(status_code=500, detail=str(e))
