from typing import Any, Optional
from pydantic import BaseModel


class TableRef(BaseModel):
    db: str
    table: str


class GenerateSQLRequest(BaseModel):
    tables: list[TableRef]
    user_request: str
    # 多轮对话历史 [{"role":"user","content":"..."}, ...]
    history: Optional[list[dict]] = None


class ExecuteSQLRequest(BaseModel):
    sql: str
    database: str
    limit: int = 5000


class SQLResult(BaseModel):
    columns: list[str]
    rows: list[list[Any]]
    row_count: int
    elapsed_ms: int
