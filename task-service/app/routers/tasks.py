from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
import httpx

from ..schemas import TaskCreate, TaskUpdate
from ..dependencies import get_db, get_current_user
from ..crud import create_task, get_task, update_task, delete_task
from ..config import NOTIFICATION_URL


router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/")
async def create_task_endpoint(
    task: TaskCreate,
    db=Depends(get_db),
    user=Depends(get_current_user)
):

    new_task = await create_task(db, task, user["id"])

    async with httpx.AsyncClient() as client:

        await client.post(
            f"{NOTIFICATION_URL}/notify/task-created",
            json={"task_id": str(new_task["_id"])}
        )

    return {"id": str(new_task["_id"])}


@router.get("/{task_id}")
async def get_task_endpoint(
    task_id: str,
    db=Depends(get_db),
    user=Depends(get_current_user)
):

    task = await get_task(db, task_id)

    if not task:

        raise HTTPException(404, "Task not found")

    task["id"] = str(task["_id"])

    return task


@router.put("/{task_id}")
async def update_task_endpoint(
    task_id: str,
    task_update: TaskUpdate,
    db=Depends(get_db),
    user=Depends(get_current_user)
):

    updated = await update_task(
        db,
        task_id,
        task_update.dict(exclude_none=True)
    )

    return updated


@router.delete("/{task_id}")
async def delete_task_endpoint(
    task_id: str,
    db=Depends(get_db),
    user=Depends(get_current_user)
):

    result = await delete_task(db, task_id)

    if result.deleted_count == 0:

        raise HTTPException(404, "Task not found")

    return {"message": "Task deleted"}