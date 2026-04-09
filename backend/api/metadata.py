from typing import Optional

from fastapi import APIRouter, Depends, Query

from core.deps import CurrentUser
from schemas.metadata import ColumnItem, DatabaseItem, DataSourceItem, TableDetail, TableItem
from services.metadata_service import MetadataService

router = APIRouter(prefix="/api/metadata", tags=["元数据"])


def get_metadata_service() -> MetadataService:
    return MetadataService()


@router.get("/sources", response_model=list[DataSourceItem])
def get_sources(current_user: CurrentUser):
    return [
        DataSourceItem(key="hive", label="Hive"),
        DataSourceItem(key="starrocks", label="StarRocks"),
    ]


@router.get("/databases", response_model=list[DatabaseItem])
def get_databases(
    source: str = Query(..., description="hive 或 starrocks"),
    current_user: CurrentUser = None,
    svc: MetadataService = Depends(get_metadata_service),
):
    return svc.list_databases(source)


@router.get("/tables", response_model=list[TableItem])
def search_tables(
    source: str = Query(...),
    db: str = Query(..., alias="db"),
    keyword: Optional[str] = Query(None),
    current_user: CurrentUser = None,
    svc: MetadataService = Depends(get_metadata_service),
):
    return svc.search_tables(source, db, keyword)


@router.get("/columns", response_model=TableDetail)
def get_columns(
    source: str = Query(...),
    db: str = Query(..., alias="db"),
    table: str = Query(...),
    current_user: CurrentUser = None,
    svc: MetadataService = Depends(get_metadata_service),
):
    return svc.get_table_detail(source, db, table)
