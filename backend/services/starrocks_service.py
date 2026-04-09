"""StarRocks 查询服务 — 只读，带安全校验。"""

import time
from typing import Any

import pymysql
from dbutils.pooled_db import PooledDB

from config import settings
from schemas.analytics import SQLResult

FORBIDDEN_KEYWORDS = {"drop", "truncate", "delete", "update", "insert", "alter", "create", "outfile"}


def _build_pool() -> PooledDB:
    return PooledDB(
        creator=pymysql,
        maxconnections=10,
        mincached=1,
        maxcached=5,
        host=settings.starrocks_host,
        port=settings.starrocks_port,
        user=settings.starrocks_user,
        password=settings.starrocks_password,
        charset="utf8mb4",
        connect_timeout=10,
        read_timeout=settings.starrocks_read_timeout,
        autocommit=True,
        cursorclass=pymysql.cursors.Cursor,
    )


_pool: PooledDB | None = None


def _get_pool() -> PooledDB:
    global _pool
    if _pool is None:
        _pool = _build_pool()
    return _pool


class StarRocksService:
    def _validate(self, sql: str) -> None:
        stripped = sql.strip()
        if not stripped:
            raise ValueError("SQL 不能为空")
        first_word = stripped.split()[0].lower()
        if first_word != "select":
            raise ValueError(f"只允许 SELECT 查询，当前语句类型：{first_word.upper()}")
        sql_lower = sql.lower()
        for kw in FORBIDDEN_KEYWORDS:
            if kw in sql_lower:
                raise ValueError(f"SQL 包含禁止关键字：{kw.upper()}")

    def execute(self, sql: str, database: str, limit: int = 5000) -> SQLResult:
        self._validate(sql)

        # 注入 LIMIT（如果 SQL 没有 LIMIT 则追加）
        sql_stripped = sql.rstrip().rstrip(";")
        if "limit" not in sql_stripped.lower():
            sql_stripped = f"{sql_stripped} LIMIT {limit}"

        start = time.time()
        conn = _get_pool().connection()
        try:
            with conn.cursor() as cur:
                if database:
                    cur.execute(f"USE `{database}`")
                cur.execute(sql_stripped)
                rows_raw = cur.fetchall()
                columns = [d[0] for d in cur.description] if cur.description else []
        finally:
            conn.close()

        elapsed_ms = int((time.time() - start) * 1000)
        rows: list[list[Any]] = [list(r) for r in rows_raw]
        return SQLResult(columns=columns, rows=rows, row_count=len(rows), elapsed_ms=elapsed_ms)
