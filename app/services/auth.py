"""认证与用户业务逻辑"""

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.utils.security import hash_password, verify_password
from app.utils.exceptions import NotFoundException, ForbiddenException, AppException
from app.utils.logger import logger


class AuthService:
    """认证服务"""

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> User | None:
        """验证用户凭据"""
        user = db.query(User).filter(
            (User.username == username) | (User.email == username)
        ).first()

        if not user or not verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            raise ForbiddenException("用户已被禁用")
        return user

    @staticmethod
    def register_user(db: Session, user_data: UserCreate) -> User:
        """注册新用户"""
        # 检查用户名是否已存在
        if db.query(User).filter(User.username == user_data.username).first():
            raise AppException(code=400, message="用户名已被注册")

        # 检查邮箱是否已存在
        if db.query(User).filter(User.email == user_data.email).first():
            raise AppException(code=400, message="邮箱已被注册")

        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
            full_name=user_data.full_name,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        logger.info(f"新用户注册成功: {user.username} (id={user.id})")
        return user


class UserService:
    """用户服务"""

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundException(f"用户 ID={user_id} 不存在")
        return user

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> User:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise NotFoundException(f"用户 {username} 不存在")
        return user

    @staticmethod
    def list_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
        return db.query(User).offset(skip).limit(limit).all()

    @staticmethod
    def update_user(db: Session, user_id: int, user_data: UserUpdate) -> User:
        user = UserService.get_user_by_id(db, user_id)

        update_data = user_data.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = hash_password(update_data.pop("password"))

        for field, value in update_data.items():
            setattr(user, field, value)

        db.commit()
        db.refresh(user)
        logger.info(f"用户信息已更新: {user.username} (id={user.id})")
        return user

    @staticmethod
    def delete_user(db: Session, user_id: int) -> None:
        user = UserService.get_user_by_id(db, user_id)
        db.delete(user)
        db.commit()
        logger.info(f"用户已删除: {user.username} (id={user_id})")
