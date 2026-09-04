"""FastAPI 应用入口"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.utils.logger import logger
from app.utils.exceptions import register_exception_handlers
from app.routers import auth, user


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理：启动时初始化，关闭时清理"""
    # 启动
    logger.info(f"🚀 {settings.APP_NAME} 启动中... 环境: {settings.APP_ENV}")

    # 开发环境自动建表（生产环境建议使用 Alembic 迁移）
    if not settings.is_production:
        from app.database import init_db
        init_db()
        logger.info("数据库表初始化完成（开发模式）")

    logger.info(f"✅ {settings.APP_NAME} 启动成功 | 监听 {settings.APP_HOST}:{settings.APP_PORT}")
    yield
    # 关闭
    logger.info(f"👋 {settings.APP_NAME} 正在关闭...")


def create_app() -> FastAPI:
    """创建并配置 FastAPI 应用"""
    app = FastAPI(
        title=settings.APP_NAME,
        description="开箱即用的 FastAPI 项目模板，集成日志、数据库、JWT 鉴权、Docker、CI/CD",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # CORS 中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册全局异常处理器
    register_exception_handlers(app)

    # 注册路由
    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(user.router, prefix="/api/v1")

    # 健康检查
    @app.get("/health", tags=["系统"], summary="健康检查")
    async def health_check():
        return {"status": "ok", "app": settings.APP_NAME, "version": "1.0.0"}

    # 根路径
    @app.get("/", tags=["系统"], summary="根路径")
    async def root():
        return {
            "message": f"欢迎使用 {settings.APP_NAME}",
            "docs": "/docs",
            "health": "/health",
        }

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.APP_DEBUG,
    )
