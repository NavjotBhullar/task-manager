import os
import jwt
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from models import NotificationType, NotifyTaskRequest

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
SENDGRID_FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@taskmanager.com")

#JWT
def verify_token(token: str):
    try:
        payload = jwt.decode(token,SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception:
        return None
    

#Email Templates

def build_email_content(notification_type: NotificationType, task_id: str) -> str:
    if notification_type == NotificationType.TASK_ASSIGNED:
        return f"You have been assigned a new task (ID: {task_id}). Please check your task list for details."
    elif notification_type == NotificationType.TASK_COMPLETED:
        return f"A task (ID: {task_id}) has been marked as completed. Great job!"
    elif notification_type == NotificationType.TASK_UPDATED:
        return f"A task (ID: {task_id}) has been updated. Please review the changes in your task list."
    elif notification_type == NotificationType.TASK_DELETED:
        return f"A task (ID: {task_id}) has been deleted. Please check your task list for updates."
    elif notification_type == NotificationType.TASK_OVERDUE:
        return f"A task (ID: {task_id}) is overdue. Please prioritize this task and update its status."
    else:
        return "You have a new notification regarding your tasks."
    

#Email Sending
def send_email(to_email: str, subject: str, content: str):
    if not SENDGRID_API_KEY:
        print("SendGrid API key not configured. Email not sent.")
        return True, "SendGrid API key not configured"
        
    try:
        message = Mail(
            from_email=SENDGRID_FROM_EMAIL,
            to_emails=NotifyTaskRequest.recipient_email,
            subject=subject,
            html_content=content
        )
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)

        if response.status_code in (200,201,202):
            return True, "Email sent successfully"
        return False, f"Failed to send email: {response.status_code}"

    except Exception as e:
        return False, f"Failed to send email: {str(e)}"