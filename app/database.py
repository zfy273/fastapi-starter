"""数据库连接与会话管理"""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.config import settings

# 创建数据库引擎
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.APP_DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    connect_args=connect_args,
)

# 会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#  declarative base
Base = declarative_base()


def get_db():
    """FastAPI 依赖注入：获取数据库会话"""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库表（开发环境使用，生产环境建议用 Alembic）"""
    # 导入所有模型以确保 Base.metadata 包含它们
    from app.models import user  # noqa: F401

    Base.metadata.create_all(bind=engine)
