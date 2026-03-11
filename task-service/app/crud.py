from datetime import datetime
from bson import ObjectId


async def create_task(db, task_data, user_id):

    task = {

        "title": task_data.title,
        "description": task_data.description,

        "status": "pending",

        "priority": task_data.priority.value,

        "assigned_to": None,

        "created_by": ObjectId(user_id),

        "created_at": datetime.utcnow(),

        "updated_at": datetime.utcnow(),

        "due_date": task_data.due_date,

        "tags": task_data.tags
    }

    result = await db.tasks.insert_one(task)

    task["_id"] = result.inserted_id

    return task


async def get_task(db, task_id):

    return await db.tasks.find_one({"_id": ObjectId(task_id)})


async def delete_task(db, task_id):

    return await db.tasks.delete_one({"_id": ObjectId(task_id)})


async def update_task(db, task_id, updates):

    updates["updated_at"] = datetime.utcnow()

    await db.tasks.update_one(

        {"_id": ObjectId(task_id)},
        {"$set": updates}

    )

    return await db.tasks.find_one({"_id": ObjectId(task_id)})