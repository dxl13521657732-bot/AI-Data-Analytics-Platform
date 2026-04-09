import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from core.deps import CurrentUser
from schemas.analytics import ExecuteSQLRequest, GenerateSQLRequest, SQLResult
from services.ai_service import AiService
from services.metadata_service import MetadataService
from services.starrocks_service import StarRocksService

router = APIRouter(prefix="/api/analytics", tags=["AI 指标提取"])


def get_ai_service() -> AiService:
    return AiService()


def get_sr_service() -> StarRocksService:
    return StarRocksService()


def get_meta_service() -> MetadataService:
    return MetadataService()


@router.post("/generate-sql")
async def generate_sql(
    body: GenerateSQLRequest,
    current_user: CurrentUser,
    ai_svc: AiService = Depends(get_ai_service),
    meta_svc: MetadataService = Depends(get_meta_service),
):
    """流式返回 AI 生成的 SQL（SSE 格式）"""
    # 获取选中表的 DDL
    tables_ddl = []
    for ref in body.tables:
        detail = meta_svc.get_table_detail("starrocks", ref.db, ref.table)
        tables_ddl.append({"db": ref.db, "table": ref.table, "ddl": detail.ddl or ""})

    async def event_stream():
        try:
            async for chunk in ai_svc.generate_sql_stream(
                tables_ddl=tables_ddl,
                user_request=body.user_request,
                history=body.history,
            ):
                yield chunk
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.post("/execute", response_model=SQLResult)
def execute_sql(
    body: ExecuteSQLRequest,
    current_user: CurrentUser,
    sr_svc: StarRocksService = Depends(get_sr_service),
):
    """执行 SQL（只读，有安全校验）"""
    try:
        return sr_svc.execute(body.sql, body.database, body.limit)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询执行失败：{e}")
