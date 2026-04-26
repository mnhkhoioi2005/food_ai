"""
User Endpoints
Quản lý người dùng (Admin only)
"""
from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user, get_current_admin
from app.models.user import User
from app.schemas.user import UserResponse, UserAdminUpdate, UserPreferences

router = APIRouter()


# ==================== Admin Endpoints ====================

@router.get("/", response_model=List[UserResponse])
async def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    [Admin] Lấy danh sách tất cả users
    """
    query = db.query(User)
    
    if search:
        query = query.filter(
            (User.email.ilike(f"%{search}%")) | 
            (User.full_name.ilike(f"%{search}%"))
        )
    
    if role:
        query = query.filter(User.role == role)
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    users = query.offset(skip).limit(limit).all()
    return [UserResponse.model_validate(u) for u in users]


@router.get("/count")
async def get_users_count(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    [Admin] Đếm tổng số users
    """
    total = db.query(User).count()
    active = db.query(User).filter(User.is_active == True).count()
    admins = db.query(User).filter(User.role == "admin").count()
    
    return {
        "total": total,
        "active": active,
        "inactive": total - active,
        "admins": admins,
        "users": total - admins
    }


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    [Admin] Lấy thông tin chi tiết một user
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy user"
        )
    return UserResponse.model_validate(user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserAdminUpdate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    [Admin] Cập nhật thông tin user
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy user"
        )
    
    # Không cho phép self-deactivate
    if user_id == current_admin.id and user_data.is_active == False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể tự vô hiệu hóa tài khoản của mình"
        )
    
    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    return UserResponse.model_validate(user)


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    [Admin] Xóa user (soft delete - set is_active = False)
    """
    if user_id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể xóa tài khoản của chính mình"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy user"
        )
    
    # Soft delete
    user.is_active = False
    db.commit()
    
    return {"message": "Đã vô hiệu hóa user thành công"}


# ==================== User Preferences ====================

@router.get("/{user_id}/preferences")
async def get_user_preferences(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lấy preferences của user
    """
    # User chỉ có thể xem preferences của mình, trừ admin
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không có quyền truy cập"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy user"
        )
    
    return {
        "spicy_level": user.spicy_level,
        "prefer_soup": user.prefer_soup,
        "is_vegetarian": user.is_vegetarian,
        "allergens": user.allergens or [],
        "favorite_regions": user.favorite_regions or []
    }


@router.put("/{user_id}/preferences")
async def update_user_preferences(
    user_id: int,
    preferences: UserPreferences,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cập nhật preferences của user
    """
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không có quyền truy cập"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy user"
        )
    
    update_data = preferences.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    return {"message": "Cập nhật preferences thành công"}
