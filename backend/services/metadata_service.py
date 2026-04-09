"""
元数据查询服务 — 通过公司数据平台 REST API 获取 Hive / StarRocks 库表信息。

注意：具体 API 路径和响应格式需要根据公司实际数据平台文档进行适配。
目前提供的是通用结构，你需要根据公司的 API 文档修改以下函数中的
URL 路径和响应解析逻辑。
"""

import httpx
from cachetools import TTLCache, cached
from threading import Lock

from config import settings
from schemas.metadata import ColumnItem, DatabaseItem, TableDetail, TableItem

# 60 秒 TTL 内存缓存，最多 512 条
_cache: TTLCache = TTLCache(maxsize=512, ttl=60)
_lock = Lock()


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {settings.tdata_api_token}",
        "Content-Type": "application/json",
    }


class MetadataService:
    def __init__(self):
        self.base = settings.tdata_api_base.rstrip("/")
        self.timeout = 15

    # ─── StarRocks 直连元数据（不依赖数据平台 API） ──────────────────────

    def _starrocks_conn(self):
        import pymysql
        return pymysql.connect(
            host=settings.starrocks_host,
            port=settings.starrocks_port,
            user=settings.starrocks_user,
            password=settings.starrocks_password,
            charset="utf8mb4",
            connect_timeout=10,
        )

    def _sr_list_databases(self) -> list[DatabaseItem]:
        with self._starrocks_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SHOW DATABASES")
                rows = cur.fetchall()
        return [DatabaseItem(name=r[0]) for r in rows]

    def _sr_search_tables(self, db: str, keyword: str | None) -> list[TableItem]:
        with self._starrocks_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(f"SHOW TABLES FROM `{db}`")
                rows = cur.fetchall()
        tables = [TableItem(database=db, name=r[0]) for r in rows]
        if keyword:
            kw = keyword.lower()
            tables = [t for t in tables if kw in t.name.lower()]
        return tables

    def _sr_get_table_detail(self, db: str, table: str) -> TableDetail:
        with self._starrocks_conn() as conn:
            with conn.cursor() as cur:
                # 获取 DDL
                try:
                    cur.execute(f"SHOW CREATE TABLE `{db}`.`{table}`")
                    row = cur.fetchone()
                    ddl = row[1] if row else None
                except Exception:
                    ddl = None

                # 获取列信息
                cur.execute(f"DESCRIBE `{db}`.`{table}`")
                col_rows = cur.fetchall()

        columns = []
        for r in col_rows:
            columns.append(ColumnItem(
                name=r[0],
                type=r[1],
                nullable=r[2].upper() == "YES" if len(r) > 2 else None,
                comment=r[8] if len(r) > 8 else None,
            ))
        return TableDetail(database=db, table=table, ddl=ddl, columns=columns)

    # ─── Hive 元数据（通过公司数据平台 API） ──────────────────────────────

    def _hive_list_databases(self) -> list[DatabaseItem]:
        """
        适配说明：修改下方 URL 和响应解析以匹配公司数据平台 API。
        示例请求：GET {base}/hive/databases
        示例响应：{"data": [{"name": "ods"}, ...]}
        """
        url = f"{self.base}/hive/databases"
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.get(url, headers=_headers())
            resp.raise_for_status()
        data = resp.json().get("data", [])
        return [DatabaseItem(name=d["name"]) for d in data]

    def _hive_search_tables(self, db: str, keyword: str | None) -> list[TableItem]:
        """
        适配说明：修改 URL 和解析逻辑。
        示例请求：GET {base}/hive/tables?db=ods&keyword=xxx
        """
        params = {"db": db}
        if keyword:
            params["keyword"] = keyword
        url = f"{self.base}/hive/tables"
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.get(url, params=params, headers=_headers())
            resp.raise_for_status()
        data = resp.json().get("data", [])
        return [TableItem(database=db, name=d["name"], comment=d.get("comment")) for d in data]

    def _hive_get_table_detail(self, db: str, table: str) -> TableDetail:
        """
        适配说明：修改 URL 和解析逻辑。
        示例请求：GET {base}/hive/columns?db=ods&table=xxx
        """
        url = f"{self.base}/hive/columns"
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.get(url, params={"db": db, "table": table}, headers=_headers())
            resp.raise_for_status()
        data = resp.json().get("data", {})
        columns = [
            ColumnItem(name=c["name"], type=c["type"], comment=c.get("comment"))
            for c in data.get("columns", [])
        ]
        return TableDetail(database=db, table=table, ddl=data.get("ddl"), columns=columns)

    # ─── 统一入口 ─────────────────────────────────────────────────────────

    def list_databases(self, source: str) -> list[DatabaseItem]:
        cache_key = f"dbs:{source}"
        with _lock:
            if cache_key in _cache:
                return _cache[cache_key]
        result = self._sr_list_databases() if source == "starrocks" else self._hive_list_databases()
        with _lock:
            _cache[cache_key] = result
        return result

    def search_tables(self, source: str, db: str, keyword: str | None) -> list[TableItem]:
        cache_key = f"tables:{source}:{db}:{keyword}"
        with _lock:
            if cache_key in _cache:
                return _cache[cache_key]
        result = (
            self._sr_search_tables(db, keyword)
            if source == "starrocks"
            else self._hive_search_tables(db, keyword)
        )
        with _lock:
            _cache[cache_key] = result
        return result

    def get_table_detail(self, source: str, db: str, table: str) -> TableDetail:
        cache_key = f"detail:{source}:{db}:{table}"
        with _lock:
            if cache_key in _cache:
                return _cache[cache_key]
        result = (
            self._sr_get_table_detail(db, table)
            if source == "starrocks"
            else self._hive_get_table_detail(db, table)
        )
        with _lock:
            _cache[cache_key] = result
        return result
