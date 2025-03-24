from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  
from fastapi.responses import StreamingResponse
from services.wallapop_service import fetch_wallapop_products  
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
import requests
import io

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017")
client = AsyncIOMotorClient(MONGO_URI)
db = client["wallapop_db"]

@app.get("/api/search/{query}")
async def search_products(query: str, page: str = None, min_price: float = None, max_price: float = None):
    result = await fetch_wallapop_products(query, db, page, min_price, max_price)
    return result

@app.get("/api/image/{path:path}")
async def get_image(path: str):
    try:
        image_url = f"https://cdn.wallapop.com/{path}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
        }
        response = requests.get(image_url, headers=headers, stream=True)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Imagen no encontrada")
        return StreamingResponse(io.BytesIO(response.content), media_type="image/jpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener la imagen: {str(e)}")