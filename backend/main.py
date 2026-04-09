from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from core.database import init_db
from api.router import include_routers


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="AI 数据分析平台",
    description="元数据查询 · AI 指标提取 · 业务系统表映射",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载所有路由
include_routers(app)


@app.get("/health", tags=["健康检查"])
def health():
    return {"status": "ok"}
