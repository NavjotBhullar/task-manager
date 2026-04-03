import os
from dotenv import load_dotenv

load_dotenv()

# Scraper settings
BASE_URL = os.getenv("BASE_URL")
DEFAULT_PAGES = int(os.getenv("DEFAULT_PAGES", 50))
PRICE_LIMIT = float(os.getenv("PRICE_LIMIT", 1000))