from fastapi import APIRouter, Depends
from app.dependencies import get_current_user_optional
from app.models.database import User
from app.models.schemas import SessionInfo

router = APIRouter(tags=["Session"])

@router.get("/session-info", response_model=SessionInfo)
def session_info(user: User | None = Depends(get_current_user_optional)):
    if user:
        return SessionInfo(logged_in=True, user_id=user.id, name=user.name, email=user.email)
    return SessionInfo(logged_in=False)

@router.get("/session-data")
def session_data(user: User | None = Depends(get_current_user_optional)):
    if not user:
        return {"logged_in": False, "user": None, "personalization": {"saved_recommendations": 0}}
    return {
        "logged_in": True,
        "user": {"id": user.id, "name": user.name, "email": user.email},
        "personalization": {"saved_recommendations": len(user.recommendations)}
    }

