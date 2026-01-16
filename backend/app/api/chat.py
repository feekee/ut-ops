"""
对话 API - 与 Dify 平台交互
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import httpx
import json
from loguru import logger

from app.config import settings

router = APIRouter()


class ChatMessage(BaseModel):
    """聊天消息"""
    role: str  # user / assistant
    content: str


class ChatRequest(BaseModel):
    """对话请求"""
    message: str
    conversation_id: Optional[str] = None
    user_id: str = "default_user"
    inputs: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    """对话响应"""
    answer: str
    conversation_id: str
    message_id: str
    metadata: Optional[Dict[str, Any]] = None


@router.post("/send", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """
    发送消息到 Dify Agent
    非流式响应
    """
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            payload = {
                "inputs": request.inputs or {},
                "query": request.message,
                "response_mode": "blocking",
                "user": request.user_id,
            }
            
            if request.conversation_id:
                payload["conversation_id"] = request.conversation_id
            
            response = await client.post(
                f"{settings.DIFY_API_BASE_URL}/chat-messages",
                headers={
                    "Authorization": f"Bearer {settings.DIFY_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            
            if response.status_code != 200:
                logger.error(f"Dify API error: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Dify API 错误: {response.text}"
                )
            
            data = response.json()
            
            return ChatResponse(
                answer=data.get("answer", ""),
                conversation_id=data.get("conversation_id", ""),
                message_id=data.get("message_id", ""),
                metadata=data.get("metadata"),
            )
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="请求超时")
    except Exception as e:
        logger.exception("发送消息失败")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream")
async def stream_message(request: ChatRequest):
    """
    发送消息到 Dify Agent
    流式响应 (SSE)
    """
    async def generate():
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                payload = {
                    "inputs": request.inputs or {},
                    "query": request.message,
                    "response_mode": "streaming",
                    "user": request.user_id,
                }
                
                if request.conversation_id:
                    payload["conversation_id"] = request.conversation_id
                
                async with client.stream(
                    "POST",
                    f"{settings.DIFY_API_BASE_URL}/chat-messages",
                    headers={
                        "Authorization": f"Bearer {settings.DIFY_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                ) as response:
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            yield f"{line}\n\n"
                            
        except Exception as e:
            logger.exception("流式消息失败")
            error_data = {"event": "error", "message": str(e)}
            yield f"data: {json.dumps(error_data)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: str,
    user_id: str = "default_user",
    limit: int = 20,
):
    """获取对话历史"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{settings.DIFY_API_BASE_URL}/messages",
                headers={
                    "Authorization": f"Bearer {settings.DIFY_API_KEY}",
                },
                params={
                    "conversation_id": conversation_id,
                    "user": user_id,
                    "limit": limit,
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.text
                )
            
            return response.json()
            
    except Exception as e:
        logger.exception("获取对话历史失败")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str, user_id: str = "default_user"):
    """删除对话"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.delete(
                f"{settings.DIFY_API_BASE_URL}/conversations/{conversation_id}",
                headers={
                    "Authorization": f"Bearer {settings.DIFY_API_KEY}",
                },
                params={"user": user_id}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.text
                )
            
            return {"status": "deleted", "conversation_id": conversation_id}
            
    except Exception as e:
        logger.exception("删除对话失败")
        raise HTTPException(status_code=500, detail=str(e))
