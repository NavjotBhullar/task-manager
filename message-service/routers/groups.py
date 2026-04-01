from fastapi import APIRouter, Depends
from database import groups_collection
from dependencies import get_current_user
from bson import ObjectId

router = APIRouter(prefix="/groups")


@router.post("/create")
async def create_group(data: dict, user=Depends(get_current_user)):

    group = {
        "name": data["name"],
        "members": data["members"],
        "created_by": user["user_id"]
    }

    res = await groups_collection.insert_one(group)

    return {"group_id": str(res.inserted_id)}

@router.post("/add-user")
async def add_user(data: dict, user=Depends(get_current_user)):

    await groups_collection.update_one(
        {"_id": ObjectId(data["group_id"])},
        {"$addToSet": {"members": data["user_id"]}}
    )

    return {"message": "User added"}