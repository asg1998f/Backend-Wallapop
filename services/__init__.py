import requests
from typing import List, Dict
from motor.motor_asyncio import AsyncIOMotorDatabase
import datetime

API_URL = "https://api.wallapop.com/api/v3/search"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Origin": "https://es.wallapop.com",
    "Referer": "https://es.wallapop.com/",
}

CACHE = {}

async def fetch_wallapop_products(query: str, db: AsyncIOMotorDatabase) -> List[Dict[str, str]]:
    await db.searches.insert_one({"query": query, "timestamp": datetime.datetime.utcnow()})
    if query in CACHE:
        print(f"Usando caché para: {query}")
        return CACHE[query]
    params = {
        "keywords": query,
        "category_id": "17000",  
        "latitude": "40.41956",  
        "longitude": "-3.69196",  
        "source": "suggester"
    }
    try:
        response = requests.get(API_URL, params=params, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        print("Respuesta de la API:", data)
        products = data.get("search_objects", [])
        result = [
            {
                "title": p.get("title", "Sin título"),
                "price": f"{p.get('price', {}).get('amount', 0)} {p.get('price', {}).get('currency', 'EUR')}",
                "link": f"https://es.wallapop.com/item/{p.get('id', '')}"
            }
            for p in products
        ]
        CACHE[query] = result
        return result
    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con Wallapop: {e}")
        return []