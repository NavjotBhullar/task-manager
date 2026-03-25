from fastapi import APIRouter, HTTPException
from app.schemas.group import GroupCreate
from app.db.mongo import groups_collection
from bson import ObjectId

router = APIRouter()


@router.post("/create")
async def create_group(group: GroupCreate):
    group_data = group.model_dump()

    if "members" not in group_data:
        group_data["members"] = []

    result = await groups_collection.insert_one(group_data)

    return {"msg": "Group created", "group_id": str(result.inserted_id)}


@router.post("/add")
async def add_member(group_id: str, username: str):
    result = await groups_collection.update_one(
        {"_id": ObjectId(group_id)}, {"$addToSet": {"members": username}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Group not found")

    return {"msg": f"{username} added to group"}


@router.get("/")
async def get_groups():
    groups = await groups_collection.find().to_list(100)

    for g in groups:
        g["_id"] = str(g["_id"])

        if "members" not in g:
            g["members"] = []

        if "name" not in g:
            g["name"] = "Unnamed Group"

    return groups

@router.post("/add-member")
async def add_member(data: dict):
    await groups_collection.update_one(
        {"name": data["group"]},
        {"$addToSet": {"members": data["member"]}}
    )
    return {"msg": "Member added"}


@router.post("/remove-member")
async def remove_member(data: dict):
    await groups_collection.update_one(
        {"name": data["group"]},
        {"$pull": {"members": data["member"]}}
    )
    return {"msg": "Member removed"}