from pydantic import BaseModel
from config.settings import DEFAULT_PAGES


class ScrapeRequest(BaseModel):
    pages: int = DEFAULT_PAGES


class Book(BaseModel):
    title: str
    price: float
    rating: str
    product_url: str
    slug: str
    description: str
    category: str
    availability: str
    image_url: str