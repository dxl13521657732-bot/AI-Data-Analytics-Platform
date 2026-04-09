from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator


class RegisterRequest(BaseModel):
    username: str
    password: str
    email: Optional[str] = None

    @field_validator("username")
    @classmethod
    def username_valid(cls, v: str) -> str:
        if len(v) < 3 or len(v) > 50:
            raise ValueError("用户名长度须在 3-50 字符之间")
        return v

    @field_validator("password")
    @classmethod
    def password_valid(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("密码长度须至少 6 位")
        return v


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserInfo"


class UserInfo(BaseModel):
    id: int
    username: str
    email: Optional[str]
    role: str
    is_approved: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UpdateRoleRequest(BaseModel):
    role: str

    @field_validator("role")
    @classmethod
    def role_valid(cls, v: str) -> str:
        if v not in ("admin", "editor", "viewer"):
            raise ValueError("角色须为 admin / editor / viewer")
        return v


TokenResponse.model_rebuild()
