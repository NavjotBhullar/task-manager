from services.user.database import users_collection, tasks_collection
from bson import ObjectId


async def get_user(user_id: str):
    user = await users_collection.find_one(
        {"_id": ObjectId(user_id)}
    )

    if user:
        user["id"] = str(user["_id"])
        user.pop("_id")

    return user


async def update_user(user_id: str, data: dict):

    await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": data}
    )

    return await get_user(user_id)


async def assign_task(user_id: str, task: dict):

    # add relation to user
    task["user_id"] = user_id

    # insert task
    result = await tasks_collection.insert_one(task)

    task_id = str(result.inserted_id)

    # update user with task reference
    await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$push": {"task_ids": task_id}}
    )

    return task_id