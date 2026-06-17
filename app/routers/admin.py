from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.fishing_log import FishingLog
from app.schemas.user import UserResponse
from app.utils.dependencies import get_admin_user

router = APIRouter(prefix="/api/admin", tags=["Admin"])

@router.get("/users", response_model=list[UserResponse])
async def list_users(db: Session = Depends(get_db), admin=Depends(get_admin_user)):
    return db.query(User).all()

@router.get("/stats/overview")
async def overview(db: Session = Depends(get_db), admin=Depends(get_admin_user)):
    return {
        "total_users": db.query(User).count(),
        "total_logs": db.query(FishingLog).count(),
        "public_logs": db.query(FishingLog).filter(FishingLog.is_public == True).count(),
    }

@router.put("/users/{user_id}/activate")
async def toggle_user(user_id: int, db: Session = Depends(get_db), admin=Depends(get_admin_user)):
    from fastapi import HTTPException
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자 없음")
    user.is_active = not user.is_active
    db.commit()
    return {"is_active": user.is_active}
