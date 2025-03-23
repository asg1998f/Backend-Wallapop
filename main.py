from fastapi import FastAPI
from services.wallapop_service import fetch_wallapop_products  
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()
app = FastAPI()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017")
client = AsyncIOMotorClient(MONGO_URI)
db = client["wallapop_db"]

@app.get("/api/search/{query}")
async def search_products(query: str, page: str = None, min_price: float = None, max_price: float = None):
    result = await fetch_wallapop_products(query, db, page, min_price, max_price)
    return result



