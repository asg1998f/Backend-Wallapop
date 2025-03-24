import requests
from typing import Dict
from motor.motor_asyncio import AsyncIOMotorDatabase
import datetime
import uuid
import re

API_URL = "https://api.wallapop.com/api/v3/search"

HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "es,es-ES;q=0.9",
    "Connection": "keep-alive",
    "Host": "api.wallapop.com",
    "Origin": "https://es.wallapop.com",
    "Referer": "https://es.wallapop.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "X-AppVersion": "84380",
    "X-DeviceID": str(uuid.uuid4()),
    "X-DeviceOS": "0",
    "Sec-Ch-Ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
}

def create_slug(title: str) -> str:
    """Convierte el título en un slug limpio (minúsculas, sin espacios ni caracteres especiales)."""
    slug = title.lower().replace(" ", "-").replace(",", "").replace(".", "")
    return slug

def extract_numeric_id_from_image_url(image_url: str) -> str:
    """Extrae el ID numérico de la URL de la imagen (por ejemplo, c10420p1115169485 -> 1115169485)."""
    match = re.search(r"c10420p(\d+)", image_url)
    if match:
        return match.group(1)  
    return None

async def fetch_wallapop_products(query: str, db: AsyncIOMotorDatabase, page: str = None, min_price: float = None, max_price: float = None) -> Dict:
    await db.searches.insert_one({"query": query, "timestamp": datetime.datetime.now(datetime.timezone.utc)})
    params = {
        "source": "suggester",
        "keywords": query,
    }
    if page:
        params["next_page"] = page
    if min_price is not None:
        params["min_sale_price"] = min_price
    if max_price is not None:
        params["max_sale_price"] = max_price

    try:
        print(f"Enviando petición a {API_URL} con params={params}")
        response = requests.get(API_URL, params=params, headers=HEADERS)
        print(f"Código de respuesta: {response.status_code}")
        response.raise_for_status()
        data = response.json()
        
        section = data.get("data", {}).get("section", {})
        products = []
        next_page = data.get("meta", {}).get("next_page", None)
        if section.get("type") == "organic_search_results":
            products = section.get("payload", {}).get("items", [])
        
        result = []
        for p in products:
            print(f"Producto completo: {p}")  
            title = p.get("title", "Sin título")
            image_url = p.get("images", [{}])[0].get("urls", {}).get("medium", "")
            id_fallback = p.get("id", "")
            
            numeric_id = extract_numeric_id_from_image_url(image_url) if image_url else None
            print(f"Producto: {title}, numeric_id: {numeric_id}, id: {id_fallback}, image_url: {image_url}")
            
            if numeric_id:
                link = f"https://es.wallapop.com/item/{create_slug(title)}-{numeric_id}"
            else:
                link = f"https://es.wallapop.com/item/{create_slug(title)}-{id_fallback}"
            
            product = {
                "title": title,
                "price": f"{p.get('price', {}).get('amount', 0)} {p.get('price', {}).get('currency', 'EUR')}",
                "link": link,
                "image": image_url,
                "location": f"{p.get('location', {}).get('city', 'Desconocido')}, {p.get('location', {}).get('region', 'Desconocido')}"
            }
            result.append(product)
        
        return {"products": result, "next_page": next_page}
    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con Wallapop: {e}")
        return {"products": [], "next_page": None}
    except ValueError as e:
        print(f"Error al parsear JSON: {e}")
        return {"products": [], "next_page": None}