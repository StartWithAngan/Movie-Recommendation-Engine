from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import get_current_user_id, get_db
from app.schemas.schemas import TokenResponse, UserLogin, UserOut, UserRegister
from app.services.auth_service import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegister, db=Depends(get_db)):
    existing = await db.users.find_one({"email": payload.email.lower()})
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    result = await db.users.insert_one({
        "email": payload.email.lower(),
        "password_hash": hash_password(payload.password),
        "display_name": payload.display_name.strip(),
    })
    return TokenResponse(access_token=create_access_token(str(result.inserted_id)))

@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin, db=Depends(get_db)):
    user = await db.users.find_one({"email": payload.email.lower()})
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return TokenResponse(access_token=create_access_token(str(user["_id"])))

@router.get("/me", response_model=UserOut)
async def me(user_id: str = Depends(get_current_user_id), db=Depends(get_db)):
    from bson import ObjectId
    user = await db.users.find_one({"_id": ObjectId(user_id)}, {"password_hash": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserOut(id=str(user["_id"]), email=user["email"], display_name=user["display_name"])
