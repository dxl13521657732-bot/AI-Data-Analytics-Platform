from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_db
from core.deps import CurrentUser, require_role
from core.security import create_access_token, hash_password, verify_password
from models.user import User
from schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UpdateRoleRequest,
    UserInfo,
)

router = APIRouter(prefix="/api/auth", tags=["认证"])
admin_router = APIRouter(prefix="/api/admin", tags=["管理员"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == body.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    if body.email and db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=400, detail="邮箱已被使用")

    # 第一个注册的用户自动成为 admin 并且直接审批通过
    is_first = db.query(User).count() == 0
    user = User(
        username=body.username,
        email=body.email,
        hashed_password=hash_password(body.password),
        role="admin" if is_first else "viewer",
        is_approved=is_first,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "注册成功" + ("，您是第一个用户已自动设为管理员" if is_first else "，请等待管理员审批")}


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == body.username).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="账号已禁用")
    if not user.is_approved:
        raise HTTPException(status_code=403, detail="账号待管理员审批，请联系管理员")

    token = create_access_token({"sub": user.id, "role": user.role})
    return TokenResponse(access_token=token, user=UserInfo.model_validate(user))


@router.get("/me", response_model=UserInfo)
def get_me(current_user: CurrentUser):
    return current_user


# ─── 管理员接口 ──────────────────────────────────────────────────────

@admin_router.get("/users", response_model=List[UserInfo])
def list_users(
    current_user: Annotated[User, Depends(require_role("admin"))],
    db: Session = Depends(get_db),
    approved: bool = None,
):
    q = db.query(User)
    if approved is not None:
        q = q.filter(User.is_approved == approved)
    return q.order_by(User.created_at.desc()).all()


@admin_router.post("/users/{user_id}/approve")
def approve_user(
    user_id: int,
    current_user: Annotated[User, Depends(require_role("admin"))],
    db: Session = Depends(get_db),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    user.is_approved = True
    db.commit()
    return {"message": f"用户 {user.username} 已审批通过"}


@admin_router.put("/users/{user_id}/role")
def update_role(
    user_id: int,
    body: UpdateRoleRequest,
    current_user: Annotated[User, Depends(require_role("admin"))],
    db: Session = Depends(get_db),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    user.role = body.role
    db.commit()
    return {"message": f"用户 {user.username} 角色已更新为 {body.role}"}


@admin_router.delete("/users/{user_id}")
def disable_user(
    user_id: int,
    current_user: Annotated[User, Depends(require_role("admin"))],
    db: Session = Depends(get_db),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="不能禁用自己的账号")
    user.is_active = False
    db.commit()
    return {"message": f"用户 {user.username} 已禁用"}
