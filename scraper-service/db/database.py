import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("BOOKS_COLLECTION")

client = MongoClient(MONGO_URI)

db = client[DB_NAME]

books_collection = db[COLLECTION_NAME]

#  unique index
try:
    books_collection.create_index("slug", unique=True)
except:
    pass