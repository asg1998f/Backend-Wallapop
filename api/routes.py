from fastapi import APIRouter, Depends
from services.wallapop_service import fetch_wallapop_products
from models.product import Product
from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase
from database.mongo import get_db

router = APIRouter(prefix="/api", tags=["search"])

@router.get("/search/{query}", response_model=List[Product])
async def search_products(query: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    return await fetch_wallapop_products(query, db)

@router.get("/")
async def root():
    return {"message": "Wallapop Scraper"}