from fastapi import APIRouter, Query
from models.schema import ScrapeRequest
from services.scraper_service import scrape_books
from db.database import books_collection

router = APIRouter()


@router.post("/scrape")
def scrape(data: ScrapeRequest):
    count = scrape_books(data.pages)
    return {
        "message": "Books stored successfully",
        "collection": "navjot_books",
        "inserted": count
    }


# 🔹 Get all books
@router.get("/books")
def get_books(limit: int = 10):
    books = list(books_collection.find({}, {"_id": 0}).limit(limit))
    return {"data": books}


# 🔹 Count
@router.get("/books/count")
def count_books():
    return {"total": books_collection.count_documents({})}


# 🔹 Filter by category
@router.get("/books/category")
def get_by_category(category: str):
    books = list(books_collection.find({"category": category}, {"_id": 0}))
    return {"data": books}


# 🔹 Filter by rating
@router.get("/books/rating")
def get_by_rating(rating: str):
    books = list(books_collection.find({"rating": rating}, {"_id": 0}))
    return {"data": books}


# 🔹 Search by title
@router.get("/books/search")
def search_books(q: str = Query(...)):
    books = list(
        books_collection.find(
            {"title": {"$regex": q, "$options": "i"}},
            {"_id": 0}
        )
    )
    return {"data": books}


# 🔹 Get single book by slug
@router.get("/books/{slug}")
def get_book(slug: str):
    book = books_collection.find_one({"slug": slug}, {"_id": 0})
    return {"data": book}