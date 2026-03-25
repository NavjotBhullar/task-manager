from celery_app import celery_app
from sync_database import notifications_collection, users_collection
from utils import send_email
from bson import ObjectId
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os


# =========================================================
# 📄 REPORT GENERATION + EMAIL
# =========================================================
@celery_app.task
def generate_report(user_id: str):

    # 🔍 Get user (SYNC)
    user = users_collection.find_one({"_id": ObjectId(user_id)})

    if not user or not user.get("email"):
        print("❌ No email found for user")
        return

    email = user["email"]
    name = user.get("name", "User")

    # 📁 Ensure folder exists
    os.makedirs("reports", exist_ok=True)

    file_path = f"reports/report_{user_id}.pdf"

    # 🧾 Generate PDF
    c = canvas.Canvas(file_path, pagesize=letter)

    c.setFont("Helvetica", 14)
    c.drawString(100, 750, "Task Report")

    c.setFont("Helvetica", 10)
    c.drawString(100, 720, f"User: {name}")
    c.drawString(100, 700, f"User ID: {user_id}")
    c.drawString(100, 680, "Generated via Celery Worker")

    c.drawString(100, 640, "-----------------------------")
    c.drawString(100, 620, "This is your report.")

    c.save()

    print(f"📄 Report generated: {file_path}")

    # ✉️ Send email with attachment
    success, msg = send_email(
        email,
        "Your Report is Ready 📄",
        f"Hi {name},<br>Your report is attached.",
        attachment_path=file_path
    )

    if success:
        print("✅ Report emailed successfully")
    else:
        print("❌ Email failed:", msg)


# =========================================================
# 📬 PROCESS NOTIFICATION (EMAIL)
# =========================================================
@celery_app.task(bind=True, max_retries=3)
def process_notification(self, notification_id: str):

    doc = notifications_collection.find_one({"_id": ObjectId(notification_id)})

    if not doc:
        return

    success, message = send_email(
        doc["recipient_email"],
        doc["subject"],
        doc["body"]
    )

    if success:
        notifications_collection.update_one(
            {"_id": ObjectId(notification_id)},
            {
                "$set": {
                    "status": "sent",
                    "sent_at": datetime.utcnow()
                }
            }
        )
        print("✅ Notification email sent")

    else:
        notifications_collection.update_one(
            {"_id": ObjectId(notification_id)},
            {
                "$set": {
                    "status": "failed",
                    "error_message": message
                },
                "$inc": {"retry_count": 1}
            }
        )

        print("❌ Email failed, retrying...")
        raise self.retry(countdown=5)