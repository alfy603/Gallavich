from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import models, schemas
from app.security import get_current_user, get_current_admin
import datetime  # 🔥 添加这行导入
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
import bcrypt  # 🔥 添加 bcrypt 直接导入

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/users", response_model=schemas.BaseResponse)
async def get_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    username: Optional[str] = Query(None),  # 🆕 添加用户名搜索
    role: Optional[str] = Query(None),      # 🆕 添加角色筛选
    is_active: Optional[bool] = Query(None), # 🆕 添加状态筛选
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin)
):
    """获取用户列表 - 添加搜索功能"""
    skip = (page - 1) * page_size
    query = db.query(models.User)  # 🆕 使用查询对象
    
    print("=== 👥 用户搜索 ===")
    print(f"搜索参数 - username: '{username}', role: '{role}', is_active: {is_active}")
    
    # 🆕 添加搜索条件
    if username and username.strip():
        query = query.filter(models.User.name.like(f"%{username.strip()}%"))
        print(f"✅ 应用用户名搜索: '{username}'")
    
    if role and role.strip():
        query = query.filter(models.User.role == role.strip())
        print(f"✅ 应用角色筛选: '{role}'")
    
    if is_active is not None:
        query = query.filter(models.User.is_active == is_active)
        print(f"✅ 应用状态筛选: {is_active}")
    
    # 获取总数和分页数据
    total = query.count()
    users = query.offset(skip).limit(page_size).all()
    
    print(f"📊 用户搜索结果: {len(users)} 条，总计 {total} 条")
    
    user_list = []
    for user in users:
        user_list.append({
            "id": user.id,
            "name": user.name,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "video_count": len(user.videos),
            "comment_count": len(user.comments)
        })
    
    return {
        "code": 200,
        "message": "获取用户列表成功",
        "data": {
            "users": user_list,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "pages": (total + page_size - 1) // page_size
            }
        }
    }

@router.put("/users/{user_id}/role", response_model=schemas.BaseResponse)
async def update_user_role(
    user_id: int,
    role_data: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin)
):
    """更新用户角色"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    if role_data.get("role") not in ["admin", "user"]:
        raise HTTPException(status_code=400, detail="角色参数错误")
    
    user.role = role_data["role"]
    db.commit()
    
    return {
        "code": 200,
        "message": "用户角色更新成功",
        "data": None
    }

@router.put("/users/{user_id}/status", response_model=schemas.BaseResponse)
async def update_user_status(
    user_id: int,
    status_data: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin)
):
    """更新用户状态"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    user.is_active = status_data.get("is_active", True)
    db.commit()
    
    return {
        "code": 200,
        "message": "用户状态更新成功",
        "data": None
    }


    

@router.get("/videos", response_model=schemas.BaseResponse)
async def get_videos(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    vod_name: Optional[str] = Query(None),
    type_name: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin)
):
    """获取视频列表 - 使用测试路由验证的逻辑"""
    skip = (page - 1) * page_size
    
    print("🎯" * 20)
    print(f"🎯 主搜索路由被调用!")
    print(f"🎯 vod_name: '{vod_name}', type_name: '{type_name}'")
    print("🎯" * 20)
    
    # 🆕 使用测试路由验证过的逻辑
    query = db.query(models.MovDetail)
    
    # 视频名称搜索
    if vod_name and vod_name.strip():
        query = query.filter(models.MovDetail.vod_name.like(f"%{vod_name.strip()}%"))
        print(f"✅ 应用视频搜索: '{vod_name}'")
    
    # 分类搜索
    if type_name and type_name.strip():
        query = query.filter(models.MovDetail.type_name == type_name.strip())
        print(f"✅ 应用分类搜索: '{type_name}'")
    
    # 获取总数
    total = query.count()
    print(f"📊 数据库查询找到 {total} 条数据")
    
    # 获取分页数据
    videos = query.order_by(models.MovDetail.id.desc()).offset(skip).limit(page_size).all()
    
    print(f"📺 返回 {len(videos)} 条数据")
    
    video_list = []
    for video in videos:
        video_list.append({
            "id": video.id,
            "vod_name": video.vod_name,
            "vod_pic": video.vod_pic,
            "vod_remarks": video.vod_remarks,
            "type_name": video.type_name,
            "vod_time": video.vod_time.isoformat() if video.vod_time else None,
            "comment_count": len(video.comments)
        })
    
    # 🆕 显示返回的第一条数据标题
    if video_list:
        print(f"📝 第一条数据标题: '{video_list[0]['vod_name']}'")
    
    return {
        "code": 200,
        "message": "获取视频列表成功",
        "data": {
            "videos": video_list,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "pages": (total + page_size - 1) // page_size
            }
        }
    }

@router.delete("/videos/{video_id}", response_model=schemas.BaseResponse)
async def delete_video_admin(
    video_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin)
):
    """
    管理员删除视频
    """
    try:
        print(f"🗑️ 删除视频请求 - 视频ID: {video_id}")
        
        # 查找视频
        video = db.query(models.MovDetail).filter(models.MovDetail.id == video_id).first()
        if not video:
            print(f"❌ 视频不存在: {video_id}")
            raise HTTPException(status_code=404, detail="视频不存在")
        
        print(f"✅ 找到视频: {video.vod_name} (ID: {video.id})")
        
        # 先删除相关的评论（如果有外键约束）
        comments = db.query(models.Comment).filter(models.Comment.movdetail_id == video_id).all()
        if comments:
            print(f"🗑️ 删除相关评论: {len(comments)} 条")
            for comment in comments:
                db.delete(comment)
        
        # 删除视频
        db.delete(video)
        db.commit()
        
        print(f"✅ 视频删除成功: {video_id}")
        
        return {
            "code": 200,
            "message": "视频删除成功",
            "data": None
        }
        
    except Exception as e:
        db.rollback()
        print(f"❌ 删除视频失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"删除视频失败: {str(e)}"
        )

# 在 admin.py 的 get_comments 函数中修复时间
@router.get("/comments", response_model=schemas.BaseResponse)
async def get_comments(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    content: Optional[str] = Query(None),
    username: Optional[str] = Query(None),  
    vod_name: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin)
):
    """获取评论列表 - 修复时间显示"""
    skip = (page - 1) * page_size
    query = db.query(models.Comment)
    
    # 搜索条件保持不变...
    if content and content.strip():
        query = query.filter(models.Comment.body.like(f"%{content.strip()}%"))
    
    if username and username.strip():
        query = query.join(models.User).filter(models.User.name.like(f"%{username.strip()}%"))
    
    if vod_name and vod_name.strip():
        query = query.join(models.MovDetail).filter(models.MovDetail.vod_name.like(f"%{vod_name.strip()}%"))
    
    total = query.count()
    comments = query.order_by(models.Comment.timestamp.desc()).offset(skip).limit(page_size).all()
    
    comment_list = []
    for comment in comments:
        # 🔥 修复：UTC时间转北京时间
        display_time = "未知时间"
        if comment.timestamp:
            from datetime import timedelta
            beijing_time = comment.timestamp + timedelta(hours=8)
            display_time = beijing_time.strftime('%Y-%m-%d %H:%M:%S')
        
        comment_list.append({
            "id": comment.id,
            "body": comment.body,
            "user_name": comment.user.name,
            "vod_name": comment.movdetail.vod_name if comment.movdetail else "未知视频",
            "timestamp": display_time,  # 🔥 使用转换后的时间
            "is_reply": comment.replied_id is not None
        })
    
    return {
        "code": 200,
        "message": "获取评论列表成功",
        "data": {
            "comments": comment_list,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "pages": (total + page_size - 1) // page_size
            }
        }
    }

@router.delete("/comments/{comment_id}", response_model=schemas.BaseResponse)
async def delete_comment_admin(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin)
):
    """管理员删除评论"""
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    
    # 如果是父评论，同时删除所有回复
    if comment.replies:
        for reply in comment.replies:
            db.delete(reply)
    
    db.delete(comment)
    db.commit()
    
    return {
        "code": 200,
        "message": "评论删除成功",
        "data": None
    }

# 在 admin.py 的 get_stats 函数中修复今日统计
@router.get("/stats", response_model=schemas.BaseResponse)
async def get_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin)
):
    """获取统计数据 - 修复时间筛选"""
    user_count = db.query(models.User).count()
    video_count = db.query(models.MovDetail).count()
    comment_count = db.query(models.Comment).count()
    live_count = db.query(models.LiveStream).count()
    
    # 🔥 修复：使用北京时间计算今日统计
    from datetime import datetime, timedelta
    # 获取当前北京时间（UTC+8）
    now = datetime.utcnow() + timedelta(hours=8)
    today_start = datetime(now.year, now.month, now.day)
    # 转换为UTC时间用于数据库查询
    today_start_utc = today_start - timedelta(hours=8)
    today_end_utc = today_start_utc + timedelta(days=1)
    
    print(f"📊 统计时间范围 - 北京时间: {today_start} 到 {today_start + timedelta(days=1)}")
    print(f"📊 统计时间范围 - UTC时间: {today_start_utc} 到 {today_end_utc}")
    
    today_users = db.query(models.User).filter(
        models.User.created_at >= today_start_utc,
        models.User.created_at < today_end_utc
    ).count()
    
    today_comments = db.query(models.Comment).filter(
        models.Comment.timestamp >= today_start_utc,
        models.Comment.timestamp < today_end_utc
    ).count()
    
    return {
        "code": 200,
        "message": "获取统计数据成功",
        "data": {
            "user_count": user_count,
            "video_count": video_count,
            "comment_count": comment_count,
            "live_count": live_count,
            "today_users": today_users,
            "today_comments": today_comments
        }
    }
    
@router.get("/debug-search")
async def debug_search(
    vod_name: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """调试搜索功能"""
    print("=== 🎯 调试搜索功能 ===")
    print(f"接收到的 vod_name: '{vod_name}'")
    
    # 测试1：直接数据库查询
    from sqlalchemy import text
    test_sql = "SELECT COUNT(*) as count FROM sakura_movdetail WHERE vod_name LIKE :name"
    result = db.execute(text(test_sql), {"name": f"%{vod_name}%"})
    direct_count = result.scalar()
    print(f"直接SQL查询结果: {direct_count} 条")
    
    # 测试2：ORM查询
    orm_query = db.query(models.MovDetail)
    if vod_name:
        orm_query = orm_query.filter(models.MovDetail.vod_name.like(f"%{vod_name}%"))
    orm_count = orm_query.count()
    print(f"ORM查询结果: {orm_count} 条")
    
    # 测试3：获取几条数据看看
    sample_data = orm_query.limit(3).all()
    print("样本数据:")
    for i, item in enumerate(sample_data):
        print(f"  {i+1}. ID:{item.id} 标题:'{item.vod_name}'")
    
    return {
        "code": 200,
        "message": f"调试完成: 搜索 '{vod_name}'",
        "data": {
            "direct_sql_count": direct_count,
            "orm_count": orm_count,
            "sample_titles": [item.vod_name for item in sample_data]
        }
    }
    
    
# 在 admin.py 末尾添加直播管理API

# 在 admin.py 的 get_live_streams_admin 函数中修复时间
@router.get("/live/streams", response_model=schemas.BaseResponse)
async def get_live_streams_admin(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    title: Optional[str] = Query(None),
    streamer: Optional[str] = Query(None),
    status: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin)
):
    """获取直播流列表 - 管理员 - 修复时间显示"""
    skip = (page - 1) * page_size
    query = db.query(models.LiveStream)
    
    print("=== 🎥 直播流搜索 ===")
    print(f"搜索参数 - title: '{title}', streamer: '{streamer}', status: {status}")
    
    # 搜索条件
    if title and title.strip():
        query = query.filter(models.LiveStream.title.like(f"%{title.strip()}%"))
        print(f"✅ 应用标题搜索: '{title}'")
    
    if streamer and streamer.strip():
        query = query.join(models.User).filter(models.User.name.like(f"%{streamer.strip()}%"))
        print(f"✅ 应用主播搜索: '{streamer}'")
    
    if status is not None:
        query = query.filter(models.LiveStream.status == status)
        print(f"✅ 应用状态筛选: {status}")
    
    # 获取总数和分页数据
    total = query.count()
    streams = query.order_by(models.LiveStream.created_time.desc()).offset(skip).limit(page_size).all()
    
    print(f"📊 直播流搜索结果: {len(streams)} 条，总计 {total} 条")
    
    stream_list = []
    for stream in streams:
        # 获取评论数量
        comment_count = db.query(models.LiveComment).filter(
            models.LiveComment.live_stream_id == stream.id
        ).count()
        
        streamer_name = stream.user.name if stream.user else "未知主播"
        
        # 🔥 修复：UTC时间转北京时间
        def convert_time(utc_time):
            if utc_time:
                from datetime import timedelta
                beijing_time = utc_time + timedelta(hours=8)
                return beijing_time.strftime('%Y-%m-%d %H:%M:%S')
            return None
        
        stream_list.append({
            "id": stream.id,
            "title": stream.title,
            "description": stream.description,
            "streamer": streamer_name,
            "streamer_id": stream.user_id,
            "status": stream.status,
            "status_text": "直播中" if stream.status == 1 else "已结束",
            "viewer_count": stream.viewer_count or 0,
            "max_viewers": stream.max_viewers or 0,
            "comment_count": comment_count,
            "stream_key": stream.stream_key,
            "created_time": convert_time(stream.created_time),  # 🔥 使用转换后的时间
            "start_time": convert_time(stream.start_time),      # 🔥 使用转换后的时间
            "end_time": convert_time(stream.end_time)           # 🔥 使用转换后的时间
        })
    
    return {
        "code": 200,
        "message": "获取直播流列表成功",
        "data": {
            "streams": stream_list,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "pages": (total + page_size - 1) // page_size
            }
        }
    }

# 在 admin.py 的 get_live_comments_admin 函数中修复时间
@router.get("/live/comments", response_model=schemas.BaseResponse)
async def get_live_comments_admin(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    content: Optional[str] = Query(None),
    username: Optional[str] = Query(None),
    stream_title: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin)
):
    """获取直播评论列表 - 修复时间显示"""
    skip = (page - 1) * page_size
    query = db.query(models.LiveComment)
    
    # 搜索条件保持不变...
    if content and content.strip():
        query = query.filter(models.LiveComment.content.like(f"%{content.strip()}%"))
    
    if username and username.strip():
        query = query.join(models.User).filter(models.User.name.like(f"%{username.strip()}%"))
    
    if stream_title and stream_title.strip():
        query = query.join(models.LiveStream).filter(models.LiveStream.title.like(f"%{stream_title.strip()}%"))
    
    total = query.count()
    comments = query.order_by(models.LiveComment.timestamp.desc()).offset(skip).limit(page_size).all()
    
    comment_list = []
    for comment in comments:
        # 🔥 修复：UTC时间转北京时间
        display_time = "未知时间"
        if comment.timestamp:
            from datetime import timedelta
            beijing_time = comment.timestamp + timedelta(hours=8)
            display_time = beijing_time.strftime('%Y-%m-%d %H:%M:%S')
        
        comment_list.append({
            "id": comment.id,
            "content": comment.content,
            "user_name": comment.user.name if comment.user else "匿名用户",
            "user_id": comment.user_id,
            "stream_title": comment.stream.title if comment.stream else "未知直播",
            "stream_id": comment.live_stream_id,
            "timestamp": display_time  # 🔥 使用转换后的时间
        })
    
    return {
        "code": 200,
        "message": "获取直播评论列表成功",
        "data": {
            "comments": comment_list,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "pages": (total + page_size - 1) // page_size
            }
        }
    }

@router.delete("/live/streams/{stream_id}", response_model=schemas.BaseResponse)
async def delete_live_stream_admin(
    stream_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin)
):
    """管理员删除直播流"""
    stream = db.query(models.LiveStream).filter(models.LiveStream.id == stream_id).first()
    if not stream:
        raise HTTPException(status_code=404, detail="直播流不存在")
    
    try:
        # 先删除相关的评论
        db.query(models.LiveComment).filter(
            models.LiveComment.live_stream_id == stream_id
        ).delete()
        
        # 删除直播流
        db.delete(stream)
        db.commit()
        
        return {
            "code": 200,
            "message": "直播流删除成功",
            "data": None
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"删除直播流失败: {str(e)}"
        )

@router.delete("/live/comments/{comment_id}", response_model=schemas.BaseResponse)
async def delete_live_comment_admin(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin)
):
    """管理员删除直播评论"""
    comment = db.query(models.LiveComment).filter(models.LiveComment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    
    try:
        db.delete(comment)
        db.commit()
        
        return {
            "code": 200,
            "message": "直播评论删除成功",
            "data": None
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"删除直播评论失败: {str(e)}"
        )

@router.put("/live/streams/{stream_id}/status", response_model=schemas.BaseResponse)
async def update_live_stream_status(
    stream_id: int,
    status_data: dict,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新直播状态"""
    try:
        print(f"=== 更新直播状态 API 被调用: stream_id={stream_id} ===")
        
        # 检查管理员权限
        user_role = getattr(current_user, 'role', 'user')
        if user_role != 'admin':
            raise HTTPException(
                status_code=403,
                detail="需要管理员权限"
            )
        
        stream = db.query(models.LiveStream).filter(models.LiveStream.id == stream_id).first()
        if not stream:
            raise HTTPException(
                status_code=404,
                detail="直播不存在"
            )
        
        new_status = status_data.get('status')
        if new_status not in [0, 1]:
            raise HTTPException(
                status_code=400,
                detail="状态值无效，必须是 0 或 1"
            )
        
        # 更新状态
        stream.status = new_status
        if new_status == 0:  # 结束直播
            stream.end_time = datetime.datetime.utcnow()
        else:  # 重新开启直播
            stream.start_time = datetime.datetime.utcnow()
            stream.end_time = None
        
        db.commit()
        
        action = "开启" if new_status == 1 else "关闭"
        print(f"✅ 管理员 {current_user.name} {action}了直播: {stream.title}")
        
        return {
            'code': 200,
            'message': f'直播状态已{action}'
        }
        
    except Exception as e:
        db.rollback()
        print(f"更新直播状态错误: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f'更新直播状态失败: {str(e)}'
        )

# 用户管理 - 添加用户
# 在 admin.py 的 create_user 函数中修改密码处理部分

@router.post("/users", response_model=schemas.BaseResponse)
async def create_user(
    user_data: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin)
):
    """创建新用户 - 修复密码长度问题"""
    try:
        print(f"🎯 创建用户请求: {user_data}")
        
        # 验证必填字段
        required_fields = ["name", "password"]
        for field in required_fields:
            if field not in user_data or not user_data[field]:
                raise HTTPException(
                    status_code=400, 
                    detail=f"缺少必填字段: {field}"
                )
        
        # 检查用户名是否已存在
        existing_user = db.query(models.User).filter(
            models.User.name == user_data["name"]
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="用户名已存在"
            )
        
        password = user_data["password"]
        if len(password) < 6:
            raise HTTPException(
                status_code=400,
                detail="密码长度至少6位"
            )
        
        # 🔥 修复：处理密码长度限制
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            print(f"⚠️ 密码字节长度 {len(password_bytes)} > 72，进行截断")
            # 截断到 72 字节
            truncated_bytes = password_bytes[:72]
            password = truncated_bytes.decode('utf-8', errors='ignore')
            print(f"✅ 密码已截断为 {len(password)} 字符")
        
        # 🔥 修复：统一使用 passlib 的密码加密
        from app.security import get_password_hash
        hashed_password = get_password_hash(password)
        
        # 创建用户
        role = user_data.get("role", "user")
        if role not in ["admin", "user"]:
            role = "user"
            
        new_user = models.User(
            name=user_data["name"],
            password_hash=hashed_password,  # 使用统一的加密方式
            role=role,
            is_active=user_data.get("is_active", True),
            created_at=datetime.datetime.utcnow()
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print(f"✅ 用户创建成功: {new_user.name} (ID: {new_user.id})")
        
        return {
            "code": 200,
            "message": "用户创建成功",
            "data": {
                "id": new_user.id,
                "name": new_user.name,
                "role": new_user.role,
                "is_active": new_user.is_active
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"❌ 创建用户失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"创建用户失败: {str(e)}"
        )
def get_type_id_by_name(type_name):
    """根据分类名称获取对应的type_id"""
    type_mapping = {
        "电影": 1,
        "连续剧": 2, 
        "综艺": 3,
        "动漫": 4,
        "国产剧": 13,
        "香港剧": 14,
        "韩国剧": 16,
        "日本剧": 23,
        "欧美剧": 24
        # 可以继续添加其他映射
    }
    return type_mapping.get(type_name, 1)  # 默认返回电影的type_id
# 视频管理 - 添加视频
@router.post("/videos", response_model=schemas.BaseResponse)
async def create_video(
    video_data: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin)
):
    """创建新视频"""
    try:
        print(f"🎯 创建视频请求: {video_data}")
        
        # 验证必填字段
        required_fields = ["vod_name", "type_name"]
        for field in required_fields:
            if field not in video_data or not video_data[field]:
                raise HTTPException(
                    status_code=400, 
                    detail=f"缺少必填字段: {field}"
                )
        
        # 🔥 使用原始SQL插入，绕过模型映射问题
        from sqlalchemy import text
        
        # 获取下一个vod_id
        result = db.execute(text("SELECT COALESCE(MAX(vod_id), 0) + 1 FROM sakura_movdetail"))
        next_vod_id = result.scalar()
        
        insert_sql = text("""
            INSERT INTO sakura_movdetail 
            (vod_id, vod_name, vod_pic, vod_remarks, type_id, type_name, vod_content, vod_play_url, vod_time) 
            VALUES 
            (:vod_id, :vod_name, :vod_pic, :vod_remarks, :type_id, :type_name, :vod_content, :vod_play_url, :vod_time)
        """)
        
        params = {
            'vod_id': next_vod_id,
            'vod_name': video_data["vod_name"],
            'vod_pic': video_data.get("vod_pic", ""),
            'vod_remarks': video_data.get("vod_remarks", ""),
            'type_id': get_type_id_by_name(video_data["type_name"]),
            'type_name': video_data["type_name"],
            'vod_content': video_data.get("vod_content", ""),
            'vod_play_url': video_data.get("vod_play_url", ""),
            'vod_time': datetime.datetime.utcnow()
        }
        
        db.execute(insert_sql, params)
        db.commit()
        
        print(f"✅ 视频创建成功: {video_data['vod_name']} (ID: {next_vod_id})")
        
        return {
            "code": 200,
            "message": "视频创建成功",
            "data": {
                "id": next_vod_id,
                "vod_name": video_data["vod_name"],
                "type_name": video_data["type_name"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"❌ 创建视频失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"创建视频失败: {str(e)}"
        )
# 评论管理 - 添加评论
@router.post("/comments", response_model=schemas.BaseResponse)
async def create_comment(
    comment_data: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin)
):
    """创建新评论"""
    try:
        print(f"🎯 创建评论请求: {comment_data}")
        
        # 验证必填字段
        required_fields = ["body", "user_id", "movdetail_id"]
        for field in required_fields:
            if field not in comment_data:
                raise HTTPException(
                    status_code=400, 
                    detail=f"缺少必填字段: {field}"
                )
        
        # 验证用户是否存在
        user = db.query(models.User).filter(
            models.User.id == comment_data["user_id"]
        ).first()
        if not user:
            raise HTTPException(
                status_code=400,
                detail="用户不存在"
            )
        
        # 验证视频是否存在
        video = db.query(models.MovDetail).filter(
            models.MovDetail.id == comment_data["movdetail_id"]
        ).first()
        if not video:
            raise HTTPException(
                status_code=400,
                detail="视频不存在"
            )
        
        # 创建评论
        new_comment = models.Comment(
            body=comment_data["body"],
            user_id=comment_data["user_id"],
            movdetail_id=comment_data["movdetail_id"],
            replied_id=comment_data.get("replied_id"),
            timestamp=datetime.datetime.utcnow()
        )
        
        db.add(new_comment)
        db.commit()
        db.refresh(new_comment)
        
        print(f"✅ 评论创建成功: {new_comment.id}")
        
        return {
            "code": 200,
            "message": "评论创建成功",
            "data": {
                "id": new_comment.id,
                "body": new_comment.body,
                "user_id": new_comment.user_id,
                "movdetail_id": new_comment.movdetail_id
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"❌ 创建评论失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"创建评论失败: {str(e)}"
        )

# 获取视频分类列表（用于下拉选择）
@router.get("/video-types", response_model=schemas.BaseResponse)
async def get_video_types(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin)
):
    """获取视频分类列表"""
    try:
        # 从现有视频中提取不重复的分类
        types = db.query(models.MovDetail.type_name).distinct().all()
        type_list = [type_[0] for type_ in types if type_[0]]
        
        return {
            "code": 200,
            "message": "获取分类列表成功",
            "data": {
                "types": type_list
            }
        }
    except Exception as e:
        print(f"❌ 获取分类列表失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取分类列表失败: {str(e)}"
        )

@router.get("/users/simple", response_model=schemas.BaseResponse)
async def get_simple_users(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin)
):
    """获取简单用户列表（用于下拉选择）"""
    try:
        users = db.query(models.User).order_by(models.User.id).all()
        
        user_list = []
        for user in users:
            user_list.append({
                "id": user.id,
                "name": user.name
            })
        
        return {
            "code": 200,
            "message": "获取用户列表成功",
            "data": {
                "users": user_list
            }
        }
    except Exception as e:
        print(f"获取用户列表失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取用户列表失败: {str(e)}"
        )

@router.get("/videos/simple", response_model=schemas.BaseResponse)
async def get_simple_videos(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin)
):
    """获取简单视频列表（用于下拉选择）"""
    try:
        videos = db.query(models.MovDetail).order_by(models.MovDetail.id).limit(500).all()
        
        video_list = []
        for video in videos:
            video_list.append({
                "id": video.id,
                "vod_name": video.vod_name
            })
        
        return {
            "code": 200,
            "message": "获取视频列表成功",
            "data": {
                "videos": video_list
            }
        }
    except Exception as e:
        print(f"获取视频列表失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取视频列表失败: {str(e)}"
        )
        
# 在 admin.py 中添加以下新的接口

@router.post("/live/streams", response_model=schemas.BaseResponse)
async def create_live_stream_admin(
    stream_data: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin)
):
    """管理员创建直播流"""
    try:
        print(f"🎯 管理员创建直播请求: {stream_data}")
        
        # 验证必填字段
        required_fields = ["title", "user_id"]
        for field in required_fields:
            if field not in stream_data or not stream_data[field]:
                raise HTTPException(
                    status_code=400, 
                    detail=f"缺少必填字段: {field}"
                )
        
        # 验证用户是否存在
        user = db.query(models.User).filter(
            models.User.id == stream_data["user_id"]
        ).first()
        if not user:
            raise HTTPException(
                status_code=400,
                detail="用户不存在"
            )
        
        # 生成流密钥
        import secrets
        stream_key = secrets.token_urlsafe(12)
        
        # 创建直播记录
        live_stream = models.LiveStream(
            title=stream_data["title"],
            description=stream_data.get("description", ""),
            cover_image=stream_data.get("cover_image", "/api/imgs/live-default.jpg"),
            stream_key=stream_key,
            status=stream_data.get("status", 1),
            viewer_count=0,
            max_viewers=0,
            user_id=stream_data["user_id"],
            start_time=datetime.datetime.utcnow() if stream_data.get("status", 1) == 1 else None,
            created_time=datetime.datetime.utcnow()
        )
        
        db.add(live_stream)
        db.commit()
        db.refresh(live_stream)
        
        print(f"✅ 管理员创建直播成功: {live_stream.title} (ID: {live_stream.id})")
        
        return {
            "code": 200,
            "message": "直播创建成功",
            "data": {
                "id": live_stream.id,
                "title": live_stream.title,
                "stream_key": stream_key,
                "streamer": user.name
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"❌ 创建直播失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"创建直播失败: {str(e)}"
        )

@router.post("/live/comments", response_model=schemas.BaseResponse)
async def create_live_comment_admin(
    comment_data: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin)
):
    """管理员创建直播评论"""
    try:
        print(f"🎯 管理员创建直播评论请求: {comment_data}")
        
        # 验证必填字段
        required_fields = ["content", "user_id", "stream_id"]
        for field in required_fields:
            if field not in comment_data:
                raise HTTPException(
                    status_code=400, 
                    detail=f"缺少必填字段: {field}"
                )
        
        # 验证用户是否存在
        user = db.query(models.User).filter(
            models.User.id == comment_data["user_id"]
        ).first()
        if not user:
            raise HTTPException(
                status_code=400,
                detail="用户不存在"
            )
        
        # 验证直播是否存在
        stream = db.query(models.LiveStream).filter(
            models.LiveStream.id == comment_data["stream_id"]
        ).first()
        if not stream:
            raise HTTPException(
                status_code=400,
                detail="直播不存在"
            )
        
        # 创建评论
        live_comment = models.LiveComment(
            content=comment_data["content"],
            user_id=comment_data["user_id"],
            live_stream_id=comment_data["stream_id"],
            timestamp=datetime.datetime.utcnow()
        )
        
        db.add(live_comment)
        db.commit()
        db.refresh(live_comment)
        
        print(f"✅ 管理员创建直播评论成功: 用户={user.name}, 直播={stream.title}")
        
        return {
            "code": 200,
            "message": "评论创建成功",
            "data": {
                "id": live_comment.id,
                "content": live_comment.content,
                "user_name": user.name,
                "stream_title": stream.title
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"❌ 创建直播评论失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"创建直播评论失败: {str(e)}"
        )