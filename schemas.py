
from pydantic import BaseModel, HttpUrl
from typing import Dict, Any, Optional, List
from datetime import datetime

class VideoBase(BaseModel):
    title: str
    description: Optional[str] = None
    url: HttpUrl

class VideoCreate(VideoBase):
    pass

# 从数据库读取或返回给客户端时使用的模型
class Video(VideoBase):
    id: int
    created_at: datetime # 新增创建时间字段

    # Pydantic 配置项，允许从非字典对象(如ORM模型)创建模型
    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str
    
class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    videos: list[Video] = [] # 在获取用户信息时，可以一并获取他发布的视频

    class Config:
        from_attributes = True

# --- Token Schema ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    
class CommentBase(BaseModel):
    body: str

class CommentCreate(CommentBase):
    pass

class CommentResponse(BaseModel):
    id: int
    user_name: str
    body: str
    time: Optional[str] = None
    reply_list: List[dict] = []

    class Config:
        orm_mode = True

class CommentListResponse(BaseModel):
    code: int
    data: List[CommentResponse]
    message: str
    


class VodItem(BaseModel):
    vod_id: int
    vod_pic: Optional[str] = None
    vod_name: Optional[str] = None
    vod_remarks: Optional[str] = None

class VodListResponse(BaseModel):
    code: int
    message: str
    data: List[VodItem]

class VodDetailResponse(BaseModel):
    code: int
    data: Dict[str, Any]
    msg: str
    
class CollectionItem(BaseModel):
    vod_id: int
    vod_pic: Optional[str] = None
    vod_name: Optional[str] = None
    vod_remarks: Optional[str] = None
    type_name: Optional[str] = None

class PaginationInfo(BaseModel):
    current_page: int
    per_page: int
    total: int
    has_more: bool

class CollectionData(BaseModel):
    collections: List[CollectionItem]
    pagination: PaginationInfo

class CollectionListResponse(BaseModel):
    code: int
    message: str
    data: CollectionData

class IsCollectionResponse(BaseModel):
    code: int
    message: str
    data: int

class CollectionCreate(BaseModel):
    vod_id: int

class CollectionRemove(BaseModel):
    vod_id: int

class BaseResponse(BaseModel):
    code: int
    message: str
    data: Optional[Any] = None  # 改为 Any 类型,可以是字典或列表
    
class LiveStreamBase(BaseModel):
    title: Optional[str] = "我的直播"
    category: Optional[str] = "entertainment"

class LiveStreamBase(BaseModel):
    title: Optional[str] = "我的直播"
    category: Optional[str] = "entertainment"
    description: Optional[str] = None  # 添加缺失的字段
    tags: Optional[str] = None         # 添加缺失的字段

class LiveStreamCreate(LiveStreamBase):
    pass

class LiveStreamItem(BaseModel):
    id: int
    stream_id: int
    title: str
    cover: Optional[str] = None
    category: str
    status: int
    viewer_count: int
    streamer: str
    user_id: Optional[int] = None
    avatar: Optional[str] = None
    likes: int
    chat_count: int
    description: Optional[str] = None
    tags: Optional[str] = None
    created_time: Optional[str] = None

class LiveStreamListResponse(BaseModel):
    code: int
    data: List[LiveStreamItem]
    message: str

class LiveStreamCreateResponse(BaseModel):
    code: int
    data: Dict[str, Any]
    message: str

class LiveStreamDetail(BaseModel):
    id: int
    title: str
    category: str
    status: int
    viewer_count: int
    streamer: str
    avatar: Optional[str] = None
    play_url: Optional[str] = None
    push_url: Optional[str] = None
    stream_key: Optional[str] = None
    likes: int
    description: Optional[str] = None
    tags: Optional[str] = None
    created_at: Optional[str] = None
    cover_image: Optional[str] = None

class LiveStreamDetailResponse(BaseModel):
    code: int
    data: LiveStreamDetail
    message: str

class LiveLikeResponse(BaseModel):
    code: int
    data: Dict[str, int]
    message: str

class LiveCommentBase(BaseModel):
    stream_id: int
    content: str

class LiveCommentCreate(LiveCommentBase):
    pass

class LiveCommentItem(BaseModel):
    id: int
    username: str
    avatar: Optional[str] = None
    content: str
    time: str
    isOwn: bool
    isSystem: bool

class LiveCommentResponse(BaseModel):
    code: int
    message: str
    data: Dict[str, Any]

class LiveCommentListResponse(BaseModel):
    code: int
    data: List[LiveCommentItem]
    message: str