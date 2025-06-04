import warnings
warnings.filterwarnings("ignore", message="urllib3 v2 only supports OpenSSL 1.1.1+")

from fastapi import FastAPI
from app.database import get_db
from app.routers import chat, user
from app.crud import ensure_indexes

app = FastAPI(title="Chat Summarization API")

@app.on_event("startup")
async def startup_db_client():
    db = get_db()
    await ensure_indexes(db)

app.include_router(chat.router, prefix="/chats", tags=["chats"])
app.include_router(user.router, prefix="/users", tags=["users"]) 