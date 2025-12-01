from sqlalchemy.orm import Session
from app import models, schemas
from app.security import get_password_hash 

# === 读取操作 (Read) ===

def get_video(db: Session, video_id: int):
    """根据 ID 获取单个视频"""
    print(f"Fetching video with ID: {video_id}")
    v =  db.query(models.Video).filter(models.Video.id == video_id).first()
    return v

def get_videos(db: Session, skip: int = 0, limit: int = 100):
    """获取视频列表，支持分页"""
    return db.query(models.Video).offset(skip).limit(limit).all()

# === 创建操作 (Create) ===

def create_video(db: Session, video: schemas.VideoCreate, owner_id: int):
    """创建一个新视频"""
    video_data = video.model_dump()
    # 简单模拟：为新视频分配一个 ID
    video_data["url"] = str(video_data["url"])
    video_data["owner_id"] = owner_id
    db_video = models.Video(**video_data)    

    db.add(db_video)
    db.commit()
    db.refresh(db_video)
    return db_video

# === 更新操作 (Update) ===

def update_video(db: Session, video_id: int, video_update: schemas.VideoCreate):
    """根据 ID 更新一个视频"""
    db_video = get_video(db, video_id)
    if db_video:
        update_data = video_update.model_dump(exclude_unset=True)
        update_data['url'] = str(update_data['url'])
        for key, value in update_data.items():
            setattr(db_video, key, value)
        db.commit()
        db.refresh(db_video)
    return db_video

# === 删除操作 (Delete) ===

def delete_video(db: Session, video_id: int):
    """根据 ID 删除一个视频"""
    db_video = get_video(db, video_id)
    if db_video:
        db.delete(db_video)
        db.commit()
    return db_video


# === 用户相关的 CRUD 操作 ===

def get_user_by_username(db: Session, username: str):
    """根据用户名获取用户"""
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    """创建一个新用户"""
    # 将明文密码哈希后存储
    hashed_password = get_password_hash(user.password)
    # 创建 SQLAlchemy User 模型实例
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user