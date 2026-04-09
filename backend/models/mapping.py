from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


class BusinessSystem(Base):
    __tablename__ = "business_systems"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    owner: Mapped[str] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    modules: Mapped[list["FunctionModule"]] = relationship(
        "FunctionModule", back_populates="system", cascade="all, delete-orphan"
    )


class FunctionModule(Base):
    __tablename__ = "function_modules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    system_id: Mapped[int] = mapped_column(ForeignKey("business_systems.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    system: Mapped[BusinessSystem] = relationship("BusinessSystem", back_populates="modules")
    table_mappings: Mapped[list["TableMapping"]] = relationship(
        "TableMapping", back_populates="module", cascade="all, delete-orphan"
    )


class TableMapping(Base):
    __tablename__ = "table_mappings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    module_id: Mapped[int] = mapped_column(ForeignKey("function_modules.id"), nullable=False)
    # hive / starrocks
    data_source: Mapped[str] = mapped_column(String(20), nullable=False, default="starrocks")
    database_name: Mapped[str] = mapped_column(String(100), nullable=False)
    table_name: Mapped[str] = mapped_column(String(200), nullable=False)
    remark: Mapped[str] = mapped_column(Text, nullable=True)

    module: Mapped[FunctionModule] = relationship("FunctionModule", back_populates="table_mappings")
