from pymongo import MongoClient
import os
from dotenv import load_dotenv
from pathlib import Path

# 🔥 Force load .env
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(env_path)

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

notifications_collection = db["notifications"]
users_collection = db["users"]