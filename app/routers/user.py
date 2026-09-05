"""用户路由 - 用户信息查询与管理"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_active_admin, get_current_user
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.services.auth import UserService

router = APIRouter(prefix="/users", tags=["用户管理"])


@router.get("/me", response_model=UserResponse, summary="获取当前用户信息")
def get_me(current_user: User = Depends(get_current_user)):
    """获取当前登录用户的详细信息"""
    return current_user


@router.put("/me", response_model=UserResponse, summary="更新当前用户信息")
def update_me(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """当前用户更新自己的信息"""
    # 普通用户不能修改 is_admin 和 is_active
    update_data = user_data.model_dump(exclude_unset=True)
    update_data.pop("is_admin", None)
    update_data.pop("is_active", None)

    from app.schemas.user import UserUpdate as UU

    filtered = UU(**update_data) if update_data else UU()
    return UserService.update_user(db, current_user.id, filtered)


@router.get("", response_model=list[UserResponse], summary="获取用户列表（管理员）")
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_admin),
):
    """获取所有用户列表（仅管理员可访问）"""
    return UserService.list_users(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserResponse, summary="获取指定用户（管理员）")
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_admin),
):
    """根据 ID 获取用户信息（仅管理员）"""
    return UserService.get_user_by_id(db, user_id)


@router.put("/{user_id}", response_model=UserResponse, summary="更新用户（管理员）")
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_admin),
):
    """管理员更新任意用户信息"""
    return UserService.update_user(db, user_id, user_data)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除用户（管理员）")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_admin),
):
    """管理员删除用户"""
    UserService.delete_user(db, user_id)
