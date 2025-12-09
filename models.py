from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean  # 添加 Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import datetime

# 在 models.py 的 User 类中添加角色字段
class User(Base):
    __tablename__ = "sakura_user"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(30))
    password_hash = Column(String(128))
    role = Column(String(20), default="user")  # 添加角色字段：admin, user
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    
    # 关系定义
    videos = relationship("Video", back_populates="owner")
    comments = relationship("Comment", back_populates="user")
    collections = relationship("UserCollection", back_populates="user")
    live_streams = relationship("LiveStream", back_populates="user")
    live_comments = relationship("LiveComment", back_populates="user")
    
    @classmethod
    def create_user(cls, db, name: str, password: str, role: str = "user"):
        """创建用户的方法"""
        from app.models import get_password_hash  # 避免循环导入
        hashed_password = get_password_hash(password)
        user = cls(
            name=name,
            password_hash=hashed_password,
            role=role,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def verify_password(self, password):
        from app.models import pwd_context  # 避免循环导入
        return pwd_context.verify(password, self.password_hash)

class MovDetail(Base):
    __tablename__ = "sakura_movdetail"  # 使用原电影详情表
    
    id = Column(Integer, primary_key=True, index=True)
    vod_name = Column(String(200))
    vod_pic = Column(String(500))
    vod_remarks = Column(String(100))
    type_id = Column(Integer)
    type_name = Column(String(50))
    vod_content = Column(Text)
    vod_play_url = Column(Text)
    vod_time = Column(DateTime)
    
    comments = relationship("Comment", back_populates="movdetail")

class MovInfo(Base):
    __tablename__ = "sakura_movinfo"  # 使用原电影信息表
    
    vod_id = Column(Integer, primary_key=True, index=True)
    type_id = Column(Integer)
    type_name = Column(String(50))
    vod_name = Column(String(200))
    vod_en = Column(String(200))
    vod_time = Column(String(50))
    vod_remarks = Column(String(100))
    vod_play_from = Column(String(100))
    vod_play_url = Column(Text)

class MovType(Base):
    __tablename__ = "sakura_movtype"  # 使用原分类表
    
    type_id = Column(Integer, primary_key=True, index=True)
    type_name = Column(String(50))

class UserCollection(Base):
    __tablename__ = "sakura_user_collection"  # 使用原收藏表
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("sakura_user.id"))  # 外键指向 sakura_user
    movdetail_id_list = Column(Text, default="")
    
    user = relationship("User", back_populates="collections")

class Comment(Base):
    __tablename__ = "sakura_comment"
    
    id = Column(Integer, primary_key=True, index=True)
    body = Column(Text, nullable=False)
    # 🔥 修复：确保 timestamp 不为空，设置默认值
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # 外键关系
    user_id = Column(Integer, ForeignKey("sakura_user.id"))
    movdetail_id = Column(Integer, ForeignKey("sakura_movdetail.id"))
    replied_id = Column(Integer, ForeignKey("sakura_comment.id"), nullable=True)
    
    # 关系
    user = relationship("User", back_populates="comments")
    movdetail = relationship("MovDetail", back_populates="comments")
    replied = relationship("Comment", remote_side=[id], back_populates="replies")
    replies = relationship("Comment", back_populates="replied")

class LiveStream(Base):
    __tablename__ = "sakura_live_stream"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    cover_image = Column(String(500))
    stream_key = Column(String(100), unique=True, index=True)
    status = Column(Integer, default=1)
    viewer_count = Column(Integer, default=0)
    max_viewers = Column(Integer, default=0)
    start_time = Column(DateTime)
    created_time = Column(DateTime, default=datetime.datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    user_id = Column(Integer, ForeignKey("sakura_user.id"))
    
    user = relationship("User", back_populates="live_streams")
    comments = relationship("LiveComment", back_populates="stream")

# models.py - 修正 LiveComment 模型
class LiveComment(Base):
    __tablename__ = "sakura_live_comment"
    
    id = Column(Integer, primary_key=True, index=True)
    live_stream_id = Column(Integer, ForeignKey("sakura_live_stream.id"))  # 🔥 使用正确的字段名
    user_id = Column(Integer, ForeignKey("sakura_user.id"))
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)  # 🔥 使用 timestamp 而不是 created_time
    
    stream = relationship("LiveStream", back_populates="comments")
    user = relationship("User", back_populates="live_comments")

# 基础视频表（如果需要保留）
class Video(Base):
    __tablename__ = "videos"  # 这个可以保留为新表

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), index=True)
    description = Column(Text, nullable=True)
    url = Column(String(500), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    owner_id = Column(Integer, ForeignKey("sakura_user.id"), index=True, nullable=True)
    owner = relationship("User", back_populates="videos")


# 添加密码加密工具函数
from passlib.context import CryptContext
from sqlalchemy.orm import Session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)