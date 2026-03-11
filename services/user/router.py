from fastapi import APIRouter, HTTPException
from services.user.schemas import UserUpdate, TaskAssign
from services.user.crud import get_user, update_user, assign_task

router = APIRouter(prefix="/users", tags=["Users"])


# GET USER
@router.get("/{user_id}")
async def get_user_profile(user_id: str):

    user = await get_user(user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user


# UPDATE USER
@router.put("/{user_id}")
async def update_user_profile(user_id: str, user_data: UserUpdate):

    user = await get_user(user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    updated_user = await update_user(
        user_id,
        user_data.dict(exclude_unset=True)
    )

    if not updated_user:
        raise HTTPException(
            status_code=500,
            detail="User update failed"
        )

    return {
        "message": "User updated successfully",
        "user": updated_user
    }


# ASSIGN TASK
@router.post("/{user_id}/tasks")
async def assign_task_to_user(user_id: str, task: TaskAssign):

    user = await get_user(user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    task_id = await assign_task(user_id, task.dict())

    if not task_id:
        raise HTTPException(
            status_code=500,
            detail="Task assignment failed"
        )

    return {
        "message": "Task assigned successfully",
        "task_id": task_id
    }