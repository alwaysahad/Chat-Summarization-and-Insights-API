from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")

def get_db():
    client = AsyncIOMotorClient(MONGODB_URI)
    return client["chat_db"]

async def connect_to_mongodb():
    global client, db
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client["chat_db"]

async def close_mongodb_connection():
    if client:
        client.close() 