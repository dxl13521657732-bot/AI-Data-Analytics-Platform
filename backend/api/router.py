from fastapi import FastAPI

from api.auth import admin_router, router as auth_router
from api.metadata import router as metadata_router
from api.analytics import router as analytics_router
from api.mapping import router as mapping_router


def include_routers(app: FastAPI):
    app.include_router(auth_router)
    app.include_router(admin_router)
    app.include_router(metadata_router)
    app.include_router(analytics_router)
    app.include_router(mapping_router)
