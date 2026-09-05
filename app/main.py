"""FastAPI 应用入口"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.responses import HTMLResponse

from app.config import settings
from app.routers import auth, user
from app.utils.exceptions import register_exception_handlers
from app.utils.logger import logger


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
        docs_url=None,
        redoc_url=None,
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

    # 自定义文档页面（使用国内 CDN，避免 jsdelivr 加载问题）
    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html() -> HTMLResponse:
        return get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=app.title + " - Swagger UI",
            swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
            swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
        )

    @app.get("/redoc", include_in_schema=False)
    async def redoc_html() -> HTMLResponse:
        return get_redoc_html(
            openapi_url=app.openapi_url,
            title=app.title + " - ReDoc",
            redoc_js_url="https://unpkg.com/redoc@next/bundles/redoc.standalone.js",
        )

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
