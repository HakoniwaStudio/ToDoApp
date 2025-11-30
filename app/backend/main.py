from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.database.database import engine, Base
from backend.api import (
    tasks_router,
    categories_router,
    tags_router,
    reminders_router,
    progress_router
)

# データベーステーブルの作成
Base.metadata.create_all(bind=engine)

# FastAPIアプリケーションの作成
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

# CORS設定（フロントエンドからのアクセスを許可）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切に制限すること
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# APIルーターの登録
app.include_router(tasks_router, prefix=settings.API_PREFIX)
app.include_router(categories_router, prefix=settings.API_PREFIX)
app.include_router(tags_router, prefix=settings.API_PREFIX)
app.include_router(reminders_router, prefix=settings.API_PREFIX)
app.include_router(progress_router, prefix=settings.API_PREFIX)


@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
