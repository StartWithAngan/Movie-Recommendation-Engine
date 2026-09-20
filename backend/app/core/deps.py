from bson import ObjectId
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.services.auth_service import decode_access_token

security = HTTPBearer()

def get_db(request: Request): return request.app.state.db

def get_ml_artifacts(request: Request):
    if request.app.state.ml_artifacts is None:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Recommendation models are not loaded")
    return request.app.state.ml_artifacts

async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    user_id = decode_access_token(credentials.credentials)
    if not user_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token", headers={"WWW-Authenticate":"Bearer"})
    try: ObjectId(user_id)
    except Exception: raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid user identity")
    return user_id
