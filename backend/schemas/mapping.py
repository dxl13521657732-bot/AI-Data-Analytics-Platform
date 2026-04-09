from datetime import datetime
from typing import Optional
from pydantic import BaseModel


# ─── TableMapping ───────────────────────────────────────────────
class TableMappingCreate(BaseModel):
    data_source: str = "starrocks"
    database_name: str
    table_name: str
    remark: Optional[str] = None


class TableMappingUpdate(BaseModel):
    data_source: Optional[str] = None
    database_name: Optional[str] = None
    table_name: Optional[str] = None
    remark: Optional[str] = None


class TableMappingOut(BaseModel):
    id: int
    module_id: int
    data_source: str
    database_name: str
    table_name: str
    remark: Optional[str]

    class Config:
        from_attributes = True


# ─── FunctionModule ─────────────────────────────────────────────
class FunctionModuleCreate(BaseModel):
    name: str
    description: Optional[str] = None


class FunctionModuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class FunctionModuleOut(BaseModel):
    id: int
    system_id: int
    name: str
    description: Optional[str]
    table_mappings: list[TableMappingOut] = []

    class Config:
        from_attributes = True


# ─── BusinessSystem ─────────────────────────────────────────────
class BusinessSystemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    owner: Optional[str] = None


class BusinessSystemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    owner: Optional[str] = None


class BusinessSystemOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    owner: Optional[str]
    created_at: datetime
    modules: list[FunctionModuleOut] = []

    class Config:
        from_attributes = True


class BusinessSystemListItem(BaseModel):
    id: int
    name: str
    description: Optional[str]
    owner: Optional[str]
    created_at: datetime
    module_count: int = 0

    class Config:
        from_attributes = True
