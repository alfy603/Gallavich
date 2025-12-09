# main.py
import os
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

import uvicorn
from fastapi import FastAPI
from app.database import engine
from app import models
from app.routers import videos
from app.routers import auth
from app.routers import comments
from app.routers import vod
from app.routers import collection
from app.routers import live
from app.routers import admin
from app.routers import ai_search

# 🆕 强制清除模块缓存
import sys
import importlib

def reload_modules():
    modules_to_reload = [
        'app.routers.admin',
        'app.routers.videos', 
        'app.routers.auth',
        'app.routers.comments',
        'app.routers.vod',
        'app.routers.collection', 
        'app.routers.live'
    ]
    
    for module_name in modules_to_reload:
        if module_name in sys.modules:
            importlib.reload(sys.modules[module_name])
            print(f"🔄 已重新加载: {module_name}")

reload_modules()

# 在应用启动时，根据 ORM 模型创建数据库表
models.Base.metadata.create_all(bind=engine)

# 创建 FastAPI 应用实例
app = FastAPI(
    title="FastFlix",
    description="一个使用 FastAPI 和 SQLite 构建的迷你视频网站后端",
    version="1.0.0",
)

# 注册路由
app.include_router(videos.router)
app.include_router(auth.router)
app.include_router(comments.router)
app.include_router(vod.router)
app.include_router(collection.router)
app.include_router(live.router)
app.include_router(admin.router)
app.include_router(ai_search.router)
@app.get("/")
def read_root():
    return {"message": "Welcome to the FastFlix API!"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1", 
        port=8000,
        reload=True
    )