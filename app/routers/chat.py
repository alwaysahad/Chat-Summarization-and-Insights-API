from fastapi import APIRouter, HTTPException, Body, Depends, Query, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from app.schemas import ChatMessageCreate, ChatMessageResponse
from app.crud import insert_chat_message, get_chat_messages, delete_chat_messages
from app.llm import summarize_chat, chat_insights
from app.database import get_db
from datetime import datetime
from typing import Optional, List
import os
from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

router = APIRouter()

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

@router.post("/", response_model=dict)
async def store_chat_message(chat: ChatMessageCreate, db=Depends(get_db), user=Depends(get_current_user)):
    try:
        await insert_chat_message(chat, db)
        return {"message": "Chat stored successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{conversation_id}", response_model=list[ChatMessageResponse])
async def retrieve_chat_messages(
    conversation_id: str,
    db=Depends(get_db),
    user=Depends(get_current_user),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    keywords: Optional[str] = Query(None)
):
    keyword_list = keywords.split(",") if keywords else None
    messages = await get_chat_messages(conversation_id, db, start_date, end_date, keyword_list)
    if not messages:
        raise HTTPException(status_code=404, detail="Conversation not found")
    for msg in messages:
        msg.pop('_id', None)
        # Ensure timestamp exists and is a datetime object
        if 'timestamp' not in msg or msg['timestamp'] is None:
            msg['timestamp'] = datetime.utcnow()
        elif not isinstance(msg['timestamp'], datetime):
            try:
                msg['timestamp'] = datetime.fromisoformat(msg['timestamp'])
            except Exception:
                msg['timestamp'] = datetime.utcnow()
    return messages

@router.post("/summarize", response_model=dict)
async def summarize_chat_messages(conversation_id: str = Body(..., embed=True), db=Depends(get_db), user=Depends(get_current_user)):
    messages = await get_chat_messages(conversation_id, db)
    if not messages:
        raise HTTPException(status_code=404, detail="Conversation not found")
    message_texts = [msg["message"] for msg in messages]
    summary = await summarize_chat(message_texts)
    return {"summary": summary}

@router.delete("/{conversation_id}", response_model=dict)
async def delete_chat(conversation_id: str, db=Depends(get_db), user=Depends(get_current_user)):
    await delete_chat_messages(conversation_id, db)
    return {"message": "Chat deleted successfully"}

@router.post("/insights", response_model=dict)
async def chat_insights_endpoint(
    conversation_id: str = Body(..., embed=True),
    insight_type: str = Body(..., embed=True),
    db=Depends(get_db),
    user=Depends(get_current_user)
):
    messages = await get_chat_messages(conversation_id, db)
    if not messages:
        raise HTTPException(status_code=404, detail="Conversation not found")
    message_texts = [msg["message"] for msg in messages]
    insight = await chat_insights(message_texts, insight_type)
    return {"insight": insight} 