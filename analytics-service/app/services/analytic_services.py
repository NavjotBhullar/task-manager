from app.database.db import task_collection
from app.utils.helpers import get_period_range
from bson import ObjectId


class AnalyticsService:

    async def get_user_stats(self, user_id: str):

        user_object_id = ObjectId(user_id)

        total_tasks = await task_collection.count_documents({
            "created_by": user_object_id
        }) 

        
        completed_tasks = await task_collection.count_documents({
            "created_by": user_object_id,
            "status": "completed"
        })


        pending_tasks = await task_collection.count_documents({
            "created_by": user_object_id,
            "status": "pending"
        })
        
        in_progress_tasks = await task_collection.count_documents({
            "created_by": user_object_id,
            "status": "in_progress"
        })

        cancelled_tasks = await task_collection.count_documents({
            "created_by": user_object_id,
            "status": "cancelled"
        })


        return {
            "created_by": user_id,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "In_progress_tasks": in_progress_tasks,
            "cancelled_task": cancelled_tasks
        }


    async def get_dashboard_stats(self, period: str):

        start_date, end_date = get_period_range(period)

        total_tasks = await task_collection.count_documents({
        "created_at": {"$gte": start_date, "$lte": end_date}
        })

        completed_tasks = await task_collection.count_documents({
        "created_at": {"$gte": start_date, "$lte": end_date},
        "status": "completed"
        })

        pending_tasks = await task_collection.count_documents({
        "created_at": {"$gte": start_date, "$lte": end_date},
        "status": "pending"
        })

        in_progress_tasks = await task_collection.count_documents({
        "created_at": {"$gte": start_date, "$lte": end_date},
        "status": "in_progress"
        })

        cancelled_tasks = await task_collection.count_documents({
        "created_at": {"$gte": start_date, "$lte": end_date},
        "status": "cancelled"
        })


        return {
        "period": period,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "In_progress_tasks": in_progress_tasks,
        "Cancelled_task": cancelled_tasks
        }  


   