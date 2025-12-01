# routers/videos.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
# 注意这里的相对导入路径
from app import crud, schemas
from app.database import SessionLocal
from app.security import get_current_user 
from app import models

# 1. 创建一个 APIRouter 实例
#    这就像一个 "迷你 FastAPI" 应用
router = APIRouter(
    prefix="/videos",       # 为该路由下的所有路径添加前缀 /videos
    tags=["videos"],        # 在 API 文档中为这些端点分组
)

# 依赖项
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 2. 将原来的路径操作函数从 @app.get 变为 @router.get

@router.post("/", response_model=schemas.Video)
def create_video_endpoint(video: schemas.VideoCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # 直接调用 crud.py 中的函数
    return crud.create_video(db=db, video=video, owner_id=current_user.id)

@router.get("/", response_model=list[schemas.Video])
def read_videos_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    videos = crud.get_videos(db, skip=skip, limit=limit)
    return videos

@router.get("/{video_id}", response_model=schemas.Video)
def read_video_endpoint(video_id: int, db: Session = Depends(get_db)):
    db_video = crud.get_video(db, video_id=video_id)
    if db_video is None:
        raise HTTPException(status_code=404, detail="Video not found")
    return db_video

@router.put("/{video_id}", response_model=schemas.Video)
def update_user_video(
    video_id: int, 
    video_update: schemas.VideoCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_video = crud.get_video(db, video_id=video_id)
    if db_video is None:
        raise HTTPException(status_code=404, detail="Video not found")
    # 授权检查：确保视频的所有者是当前登录的用户
    if db_video.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this video")
    return crud.update_video(db, video_id, video_update)

@router.delete("/{video_id}", response_model=schemas.Video)
def delete_user_video(
    video_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_video = crud.get_video(db, video_id=video_id)
    if db_video is None:
        raise HTTPException(status_code=404, detail="Video not found")
    # 授权检查
    if db_video.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this video")
    return crud.delete_video(db, video_id)