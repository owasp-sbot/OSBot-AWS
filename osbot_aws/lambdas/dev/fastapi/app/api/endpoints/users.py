from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_users():
    return {"message": "Users!"}

@router.get("/user1")
async def get_specific_user():
    return {"message": "this is user1!"}
