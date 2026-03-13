from fastapi import APIRouter
from app.services.analytic_services import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])

analytics_service = AnalyticsService()

@router.get("/user/{id}/stats")
async def user_stats(id: str):
    return await analytics_service.get_user_stats(id)


@router.get("/dashboard")
async def dashboard_stats(period: str = "week"):
    return await analytics_service.get_dashboard_stats(period)
