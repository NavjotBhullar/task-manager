import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

AUTH_SERVICE_URL = os.getenv(
    "AUTH_SERVICE_URL",
    "http://localhost:8001"
)

NOTIFICATION_URL = os.getenv(
    "NOTIFICATION_URL",
    "http://localhost:8005"
)

JWT_SECRET = os.getenv("JWT_SECRET", "secret")

SERVICE_PORT = int(os.getenv("SERVICE_PORT", 8003))