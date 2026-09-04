"""认证路由 - 注册、登录、刷新令牌"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.schemas.user import UserCreate, UserResponse, Token
from app.services.auth import AuthService
from app.utils.security import create_access_token, create_refresh_token, verify_token
from app.utils.exceptions import UnauthorizedException
from app.utils.logger import logger

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="用户注册")
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """注册新用户"""
    user = AuthService.register_user(db, user_data)
    return user


@router.post("/login", response_model=Token, summary="用户登录")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """用户登录，返回 JWT 令牌（使用 OAuth2 表单格式）"""
    user = AuthService.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})

    logger.info(f"用户登录成功: {user.username}")
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh", response_model=Token, summary="刷新令牌")
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    """使用刷新令牌获取新的访问令牌"""
    try:
        payload = verify_token(refresh_token)
        if payload.get("type") != "refresh":
            raise UnauthorizedException("无效的刷新令牌")
        username = payload.get("sub")
        if not username:
            raise UnauthorizedException("令牌中缺少用户信息")
    except Exception:
        raise UnauthorizedException("刷新令牌无效或已过期")

    from app.services.auth import UserService
    user = UserService.get_user_by_username(db, username)
    if not user.is_active:
        raise UnauthorizedException("用户已被禁用")

    access_token = create_access_token(data={"sub": user.username})
    new_refresh_token = create_refresh_token(data={"sub": user.username})

    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
