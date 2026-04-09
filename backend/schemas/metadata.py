from typing import Optional
from pydantic import BaseModel


class DataSourceItem(BaseModel):
    key: str      # "hive" or "starrocks"
    label: str


class DatabaseItem(BaseModel):
    name: str


class TableItem(BaseModel):
    database: str
    name: str
    comment: Optional[str] = None
    engine: Optional[str] = None


class ColumnItem(BaseModel):
    name: str
    type: str
    comment: Optional[str] = None
    nullable: Optional[bool] = None


class TableDetail(BaseModel):
    database: str
    table: str
    ddl: Optional[str] = None
    columns: list[ColumnItem] = []
