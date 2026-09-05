"""用户相关 Pydantic 模型"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

# ---------- 请求模型 ----------


class UserCreate(BaseModel):
    """用户注册请求"""

    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=6, max_length=128, description="密码")
    full_name: str | None = Field(None, max_length=100, description="姓名")


class UserUpdate(BaseModel):
    """用户更新请求"""

    email: EmailStr | None = None
    full_name: str | None = Field(None, max_length=100)
    password: str | None = Field(None, min_length=6, max_length=128)
    is_active: bool | None = None


class UserLogin(BaseModel):
    """用户登录请求"""

    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")


# ---------- 响应模型 ----------


class UserResponse(BaseModel):
    """用户信息响应"""

    id: int
    username: str
    email: str
    full_name: str | None = None
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    """JWT 令牌响应"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """令牌数据"""

    username: str | None = None
