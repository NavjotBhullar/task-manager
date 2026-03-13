import os
from dotenv import load_dotenv

load_dotenv()

# -----------------------------
# MongoDB
# -----------------------------
MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb+srv://mohindersingh_db_user:mohinder123@cluster0.abwqeos.mongodb.net/?appName=Cluster0"
)

DB_NAME = os.getenv("DB_NAME", "task-manager")

# -----------------------------
# Service URLs
# -----------------------------
AUTH_SERVICE_URL = os.getenv(
    "AUTH_SERVICE_URL",
    "http://127.0.0.1:8001"
)

USER_SERVICE_URL = os.getenv(
    "USER_SERVICE_URL",
    "http://127.0.0.1:8002"
)

NOTIFICATION_URL = os.getenv(
    "NOTIFICATION_URL",
    "http://127.0.0.1:8005"
)

# -----------------------------
# Security
# -----------------------------
JWT_SECRET = os.getenv("JWT_SECRET", "secret")

# -----------------------------
# Service Port
# -----------------------------
SERVICE_PORT = int(os.getenv("SERVICE_PORT", 8003))