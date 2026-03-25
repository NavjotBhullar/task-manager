# from fastapi import APIRouter, HTTPException
# from app.schemas.user import UserCreate, UserLogin
# from app.db.mongo import users_collection
# from app.core.security import hash_password, verify_password, create_access_token

# router = APIRouter()


# @router.post("/register")
# async def register(user: UserCreate):
#     existing = await users_collection.find_one({"username": user.username})
#     if existing:
#         raise HTTPException(status_code=400, detail="User exists")

#     user_dict = user.dict()
#     user_dict["password"] = hash_password(user_dict["password"])

#     await users_collection.insert_one(user_dict)
#     return {"msg": "User created"}


# @router.post("/login")
# async def login(user: UserLogin):
#     db_user = await users_collection.find_one({"username": user.username})

#     if not db_user or not verify_password(user.password, db_user["password"]):
#         raise HTTPException(status_code=400, detail="Invalid credentials")

#     token = create_access_token({"user_id": user.username})
#     return {"access_token": token}


from fastapi import APIRouter, HTTPException
from app.schemas.user import UserCreate, UserLogin
from app.db.mongo import users_collection
from app.core.security import hash_password, verify_password, create_access_token

router = APIRouter()


@router.post("/register")
async def register(user: UserCreate):
    existing = await users_collection.find_one({"username": user.username})

    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    user_dict = user.dict()
    user_dict["password"] = hash_password(user_dict["password"])

    await users_collection.insert_one(user_dict)

    return {
        "message": "User registered successfully",
        "username": user.username
    }


@router.post("/login")
async def login(user: UserLogin):
    db_user = await users_collection.find_one({"username": user.username})

    # ❌ User not found
    if not db_user:
        raise HTTPException(status_code=400, detail="User not found")

    # ❌ Wrong password
    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=400, detail="Wrong password")

    # ✅ Create token
    token = create_access_token({"user_id": user.username})

    return {
        "message": "Login successful",
        "username": user.username,
        "access_token": token
    }