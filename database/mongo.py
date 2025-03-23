from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import Depends
import os

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGO_URL)
db = client.wallapop_db

async def get_db():
    yield db