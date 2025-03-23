from pydantic import BaseModel

class Product(BaseModel):
    title: str
    price: str
    link: str
    class Config:
        from_attributes = True