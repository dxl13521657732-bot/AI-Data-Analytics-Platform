from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from core.database import get_db
from core.deps import CurrentUser, require_role
from models.mapping import BusinessSystem, FunctionModule, TableMapping
from models.user import User
from schemas.mapping import (
    BusinessSystemCreate,
    BusinessSystemListItem,
    BusinessSystemOut,
    BusinessSystemUpdate,
    FunctionModuleCreate,
    FunctionModuleOut,
    FunctionModuleUpdate,
    TableMappingCreate,
    TableMappingOut,
    TableMappingUpdate,
)

router = APIRouter(prefix="/api/mapping", tags=["业务映射"])

Editor = Annotated[User, Depends(require_role("admin", "editor"))]


# ─── 业务系统 ──────────────────────────────────────────────────────────

@router.get("/systems", response_model=List[BusinessSystemListItem])
def list_systems(current_user: CurrentUser, db: Session = Depends(get_db)):
    systems = db.query(BusinessSystem).order_by(BusinessSystem.created_at.desc()).all()
    result = []
    for s in systems:
        item = BusinessSystemListItem.model_validate(s)
        item.module_count = len(s.modules)
        result.append(item)
    return result


@router.post("/systems", response_model=BusinessSystemOut, status_code=201)
def create_system(body: BusinessSystemCreate, current_user: Editor, db: Session = Depends(get_db)):
    sys = BusinessSystem(**body.model_dump())
    db.add(sys)
    db.commit()
    db.refresh(sys)
    return sys


@router.get("/systems/{system_id}", response_model=BusinessSystemOut)
def get_system(system_id: int, current_user: CurrentUser, db: Session = Depends(get_db)):
    sys = db.get(BusinessSystem, system_id)
    if not sys:
        raise HTTPException(status_code=404, detail="业务系统不存在")
    return sys


@router.put("/systems/{system_id}", response_model=BusinessSystemOut)
def update_system(
    system_id: int, body: BusinessSystemUpdate, current_user: Editor, db: Session = Depends(get_db)
):
    sys = db.get(BusinessSystem, system_id)
    if not sys:
        raise HTTPException(status_code=404, detail="业务系统不存在")
    for k, v in body.model_dump(exclude_none=True).items():
        setattr(sys, k, v)
    db.commit()
    db.refresh(sys)
    return sys


@router.delete("/systems/{system_id}", status_code=204)
def delete_system(system_id: int, current_user: Editor, db: Session = Depends(get_db)):
    sys = db.get(BusinessSystem, system_id)
    if not sys:
        raise HTTPException(status_code=404, detail="业务系统不存在")
    db.delete(sys)
    db.commit()


# ─── 功能模块 ──────────────────────────────────────────────────────────

@router.post("/systems/{system_id}/modules", response_model=FunctionModuleOut, status_code=201)
def create_module(
    system_id: int, body: FunctionModuleCreate, current_user: Editor, db: Session = Depends(get_db)
):
    if not db.get(BusinessSystem, system_id):
        raise HTTPException(status_code=404, detail="业务系统不存在")
    mod = FunctionModule(system_id=system_id, **body.model_dump())
    db.add(mod)
    db.commit()
    db.refresh(mod)
    return mod


@router.put("/modules/{module_id}", response_model=FunctionModuleOut)
def update_module(
    module_id: int, body: FunctionModuleUpdate, current_user: Editor, db: Session = Depends(get_db)
):
    mod = db.get(FunctionModule, module_id)
    if not mod:
        raise HTTPException(status_code=404, detail="功能模块不存在")
    for k, v in body.model_dump(exclude_none=True).items():
        setattr(mod, k, v)
    db.commit()
    db.refresh(mod)
    return mod


@router.delete("/modules/{module_id}", status_code=204)
def delete_module(module_id: int, current_user: Editor, db: Session = Depends(get_db)):
    mod = db.get(FunctionModule, module_id)
    if not mod:
        raise HTTPException(status_code=404, detail="功能模块不存在")
    db.delete(mod)
    db.commit()


# ─── 底层表映射 ────────────────────────────────────────────────────────

@router.post("/modules/{module_id}/tables", response_model=TableMappingOut, status_code=201)
def create_table_mapping(
    module_id: int, body: TableMappingCreate, current_user: Editor, db: Session = Depends(get_db)
):
    if not db.get(FunctionModule, module_id):
        raise HTTPException(status_code=404, detail="功能模块不存在")
    tm = TableMapping(module_id=module_id, **body.model_dump())
    db.add(tm)
    db.commit()
    db.refresh(tm)
    return tm


@router.put("/tables/{table_id}", response_model=TableMappingOut)
def update_table_mapping(
    table_id: int, body: TableMappingUpdate, current_user: Editor, db: Session = Depends(get_db)
):
    tm = db.get(TableMapping, table_id)
    if not tm:
        raise HTTPException(status_code=404, detail="映射记录不存在")
    for k, v in body.model_dump(exclude_none=True).items():
        setattr(tm, k, v)
    db.commit()
    db.refresh(tm)
    return tm


@router.delete("/tables/{table_id}", status_code=204)
def delete_table_mapping(table_id: int, current_user: Editor, db: Session = Depends(get_db)):
    tm = db.get(TableMapping, table_id)
    if not tm:
        raise HTTPException(status_code=404, detail="映射记录不存在")
    db.delete(tm)
    db.commit()
