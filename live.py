from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.database import get_db
from app import models, schemas
from app.security import get_current_user 
import secrets
import datetime
from fastapi import status

router = APIRouter(prefix="/live", tags=["live-streaming"])

# 统一的分类映射（内部值 -> 中文名）
CATEGORY_MAP = {
    'gaming': '游戏',
    'entertainment': '娱乐',
    'music': '音乐',
    'education': '知识',
    'other': '其他'
}
CATEGORY_DEFAULT = 'entertainment'

def normalize_category(raw):
    """标准化分类，支持英文/中文/数字映射，默认为 entertainment"""
    if not raw:
        return CATEGORY_DEFAULT

    raw = str(raw).strip().lower()

    # 英文映射
    en_map = {
        'gaming': 'gaming',
        'game': 'gaming',
        'entertainment': 'entertainment',
        'ent': 'entertainment',
        'music': 'music',
        'education': 'education',
        'edu': 'education',
        'other': 'other'
    }

    # 中文映射
    cn_map = {
        '游戏': 'gaming',
        '娱乐': 'entertainment',
        '音乐': 'music',
        '知识': 'education',
        '教育': 'education',
        '其他': 'other'
    }

    # 数字映射
    num_map = {
        0: 'gaming',
        1: 'entertainment',
        2: 'music',
        3: 'education',
        4: 'other'
    }

    if raw.isdigit():
        return num_map.get(int(raw), CATEGORY_DEFAULT)

    return en_map.get(raw) or cn_map.get(raw) or CATEGORY_DEFAULT

# live.py - 修正查询和响应
# 在 live.py 中修改 get_live_streams 函数
@router.get("/streams", response_model=schemas.LiveStreamListResponse)
async def get_live_streams(
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取直播流列表 - 修复时间显示"""
    try:
        print("=== 获取直播列表 API 被调用 ===")
        
        # 计算偏移量
        offset = (page - 1) * pageSize
        
        # 查询直播流
        streams = db.query(models.LiveStream).filter(
            models.LiveStream.status == 1  # 只返回活跃的直播
        ).offset(offset).limit(pageSize).all()
        
        print(f"从数据库找到 {len(streams)} 个直播流")
        
        # 构建响应数据
        stream_list = []
        for stream in streams:
            # 获取评论数量
            comment_count = db.query(models.LiveComment).filter(
                models.LiveComment.live_stream_id == stream.id
            ).count()
            
            # 🔥 修复：UTC时间转北京时间
            display_created_time = "未知时间"
            if stream.created_time:
                from datetime import timedelta
                beijing_time = stream.created_time + timedelta(hours=8)
                display_created_time = beijing_time.strftime('%H:%M')
            
            stream_data = {
                "id": stream.id,
                "stream_id": stream.id,
                "title": stream.title,
                "description": stream.description or "",
                "cover": stream.cover_image or "/api/imgs/live-default.svg",
                "category": "live",
                "status": stream.status,
                "viewer_count": stream.viewer_count or 0,
                "streamer": stream.user.name if stream.user else "未知主播",
                "avatar": "/api/imgs/avatar-default.jpg",
                "likes": 0,
                "chat_count": comment_count,
                "created_time": display_created_time  # 🔥 使用转换后的时间
            }
            stream_list.append(stream_data)
        
        return {
            "code": 200,
            "message": "获取直播列表成功",
            "data": stream_list,
            "pagination": {
                "page": page,
                "pageSize": pageSize,
                "total": len(stream_list),
                "hasMore": len(stream_list) == pageSize
            }
        }
        
    except Exception as e:
        print(f"获取直播列表错误: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"获取直播列表失败: {str(e)}")
        
def get_mock_streams():
    """获取模拟直播数据"""
    return [
        {
            'id': 1,
            'title': '王者荣耀高端局排位',
            'cover': '/api/imgs/game-live.jpg',
            'category': 'gaming',
            'status': 1,
            'viewer_count': 2345,
            'streamer': '游戏主播小明',
            'avatar': '/api/imgs/avatar1.jpg',
            'likes': 1567,
            'chat_count': 89,
            'created_time': '14:30'
        },
        {
            'id': 2,
            'title': '吉他弹唱教学直播',
            'cover': '/api/imgs/music-live.jpg',
            'category': 'music',
            'status': 1,
            'viewer_count': 892,
            'streamer': '音乐人小美',
            'avatar': '/api/imgs/avatar2.jpg',
            'likes': 234,
            'chat_count': 45,
            'created_time': '15:00'
        },
        {
            'id': 3,
            'title': 'Python编程入门教学',
            'cover': '/api/imgs/edu-live.jpg',
            'category': 'education',
            'status': 1,
            'viewer_count': 1567,
            'streamer': '程序员老师',
            'avatar': '/api/imgs/avatar3.jpg',
            'likes': 789,
            'chat_count': 123,
            'created_time': '16:00'
        }
    ]

@router.post("/stream/create", response_model=schemas.LiveStreamCreateResponse)
async def create_live_stream(
    stream_data: schemas.LiveStreamCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建直播 - 修复字段访问问题"""
    try:
        print("=== 创建直播 API 被调用 ===")
        
        print(f"🎯 当前用户ID: {current_user.id}, 用户名: {current_user.name}")
        print(f"📝 接收到的数据: {stream_data.dict()}")
        
        title = stream_data.title or '我的直播'
        description = stream_data.description or ''  # 安全访问
        tags = stream_data.tags or ''               # 安全访问
        
        # 生成流密钥
        import secrets
        stream_key = secrets.token_urlsafe(12)
        
        # 创建直播记录 - 只使用实际存在的数据库字段
        live_stream = models.LiveStream(
            title=title,
            stream_key=stream_key,
            cover_image='/api/imgs/live-default.jpg',
            status=1,
            viewer_count=0,
            max_viewers=0,
            description=description,  # 使用安全访问的值
            user_id=current_user.id,
            start_time=datetime.datetime.utcnow(),
            created_time=datetime.datetime.utcnow()
        )
        
        db.add(live_stream)
        db.commit()
        db.refresh(live_stream)
        
        print(f"✅ 直播创建成功: ID={live_stream.id}, 标题={title}")
        
        return {
            'code': 200,
            'data': {
                'stream_id': live_stream.id,
                'stream_key': stream_key,
                'push_url': f"rtmp://localhost:1935/live/{stream_key}",
                'play_url': f"http://localhost:8000/live/{stream_key}.flv",
                'title': title,
                'category': stream_data.category or 'entertainment',
                'description': description,
                'tags': tags
            },
            'message': '直播创建成功'
        }
        
    except Exception as e:
        db.rollback()
        print(f"创建直播错误: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f'创建直播失败: {str(e)}'
        )
# 在 live.py 中修改 get_live_stream_detail 函数
@router.get("/stream/{stream_id}", response_model=schemas.LiveStreamDetailResponse)
async def get_live_stream_detail(
    stream_id: int,
    db: Session = Depends(get_db)
):
    """获取直播详情 - 修复时间显示"""
    try:
        print(f"=== 获取直播详情 API 被调用: stream_id={stream_id} ===")
        
        stream = db.query(models.LiveStream).filter(models.LiveStream.id == stream_id).first()
        
        if not stream:
            raise HTTPException(
                status_code=404,
                detail="直播流不存在"
            )
        
        # 增加观看人数
        stream.viewer_count = (stream.viewer_count or 0) + 1
        db.commit()
        
        # 获取主播名称
        streamer_name = '未知主播'
        if stream.user_id:
            user = db.query(models.User).filter(models.User.id == stream.user_id).first()
            if user:
                streamer_name = user.name
        
        # 🔥 修复：UTC时间转北京时间
        display_created_time = "未知时间"
        if stream.created_time:
            from datetime import timedelta
            beijing_time = stream.created_time + timedelta(hours=8)
            display_created_time = beijing_time.strftime('%H:%M')
        
        display_created_at = "未知时间"
        if stream.created_time:
            from datetime import timedelta
            beijing_time = stream.created_time + timedelta(hours=8)
            display_created_at = beijing_time.strftime('%Y-%m-%d %H:%M')
        
        play_url = f"http://localhost:8000/live/{stream.stream_key}.flv"
        push_url = f"rtmp://localhost:1935/live/{stream.stream_key}"
        
        # 获取评论数量
        chat_count = db.query(models.LiveComment).filter(
            models.LiveComment.live_stream_id == stream.id
        ).count()
        
        stream_data = {
            'id': stream.id,
            'stream_id': stream.id,
            'title': stream.title,
            'description': stream.description or '',
            'cover': stream.cover_image or '/api/imgs/live-default.svg',
            'category': 'live',
            'status': stream.status,
            'viewer_count': stream.viewer_count,
            'streamer': streamer_name,
            'streamer_name': streamer_name,
            'avatar': '/api/imgs/avatar-default.jpg',
            'likes': 0,
            'chat_count': chat_count,
            'created_time': display_created_time,  # 🔥 使用转换后的时间
            'stream_key': stream.stream_key,
            'play_url': play_url,
            'push_url': push_url,
            'tags': '',
            'created_at': display_created_at,  # 🔥 使用转换后的时间
            'cover_image': stream.cover_image or '/api/imgs/live-default.jpg'
        }
        
        return {
            'code': 200,
            'data': stream_data,
            'message': 'success'
        }
        
    except Exception as e:
        print(f"获取直播详情错误: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f'获取直播详情失败: {str(e)}'
        )

def get_mock_stream_detail(stream_id):
    """获取模拟直播详情"""
    mock_streams = {
        1: {
            'id': 1,
            'title': '王者荣耀高端局排位',
            'category': 'gaming',
            'status': 1,
            'viewer_count': 2345,
            'streamer': '游戏主播小明',
            'avatar': '/api/imgs/avatar1.jpg',
            'play_url': 'http://example.com/live/stream1.flv',
            'push_url': 'rtmp://example.com/live/stream1',
            'stream_key': 'mock_key_1',
            'likes': 1567,
            'description': '国服最强王者带你上分！实时教学，欢迎提问交流',
            'tags': '王者荣耀,游戏,上分,教学',
            'created_at': '2024-01-10 14:30',
            'cover_image': '/api/imgs/game-live.jpg'
        },
        2: {
            'id': 2,
            'title': '吉他弹唱教学直播',
            'category': 'music',
            'status': 1,
            'viewer_count': 892,
            'streamer': '音乐人小美',
            'avatar': '/api/imgs/avatar2.jpg',
            'play_url': 'http://example.com/live/stream2.flv',
            'push_url': 'rtmp://example.com/live/stream2',
            'stream_key': 'mock_key_2',
            'likes': 234,
            'description': '零基础吉他教学，从和弦到弹唱，一步步教你成为吉他高手',
            'tags': '音乐,吉他,教学,弹唱',
            'created_at': '2024-01-10 15:00',
            'cover_image': '/api/imgs/music-live.jpg'
        },
        3: {
            'id': 3,
            'title': 'Python编程入门教学',
            'category': 'education',
            'status': 1,
            'viewer_count': 1567,
            'streamer': '程序员老师',
            'avatar': '/api/imgs/avatar3.jpg',
            'play_url': 'http://example.com/live/stream3.flv',
            'push_url': 'rtmp://example.com/live/stream3',
            'stream_key': 'mock_key_3',
            'likes': 789,
            'description': '从零开始学习Python编程，适合初学者。包含基础语法、项目实战等内容',
            'tags': '编程,Python,教学,入门',
            'created_at': '2024-01-10 16:00',
            'cover_image': '/api/imgs/edu-live.jpg'
        }
    }
    return mock_streams.get(stream_id, mock_streams[1])

@router.post("/stream/{stream_id}/like", response_model=schemas.LiveLikeResponse)
async def like_live_stream(
    stream_id: int,
    db: Session = Depends(get_db)
):
    """点赞直播 - 对应原Flask的 like_live_stream"""
    try:
        print(f"=== 点赞直播 API 被调用: stream_id={stream_id} ===")
        
        stream = db.query(models.LiveStream).filter(models.LiveStream.id == stream_id).first()
        if stream:
            # 🔥 数据库中没有 likes 字段，暂时返回模拟数据
            # TODO: 如果需要真实点赞功能，需要在数据库添加 likes 字段
            likes = 1  # 模拟点赞成功
            print(f"⚠️ 点赞功能暂未实现（数据库缺少 likes 字段），返回模拟数据")
        else:
            likes = 1  # 模拟点赞
        
        return {
            'code': 200,
            'data': {'likes': likes},
            'message': '点赞成功'
        }
        
    except Exception as e:
        print(f"点赞直播错误: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f'点赞失败: {str(e)}'
        )

@router.post("/stream/{stream_id}/end", response_model=schemas.BaseResponse)
async def end_live_stream(
    stream_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """结束直播(主播本人或管理员可结束)"""
    try:
        print(f"=== 结束直播 API 被调用: stream_id={stream_id} ===")
        
        print(f"🔍 当前用户ID: {current_user.id}, 角色: {getattr(current_user, 'role', 'user')}")
        
        stream = db.query(models.LiveStream).filter(models.LiveStream.id == stream_id).first()
        if not stream:
            raise HTTPException(
                status_code=404,
                detail="直播不存在"
            )
        
        print(f"🔍 直播信息 - ID: {stream.id}, 标题: {stream.title}, 创建者ID: {stream.user_id}")
        
        # 🔥 修改权限验证：允许主播本人或管理员操作
        user_role = getattr(current_user, 'role', 'user')
        if stream.user_id != current_user.id and user_role != 'admin':
            print(f"❌ 权限验证失败: 直播创建者ID={stream.user_id}, 当前用户ID={current_user.id}, 角色={user_role}")
            raise HTTPException(
                status_code=403,
                detail="无权限结束该直播"
            )
        
        stream.status = 0
        stream.end_time = datetime.datetime.utcnow()
        db.commit()
        
        print(f"✅ 直播结束成功: {stream_id}")
        return {
            'code': 200,
            'message': '直播已结束'
        }
        
    except Exception as e:
        db.rollback()
        print(f"结束直播错误: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f'结束直播失败: {str(e)}'
        )

@router.delete("/stream/{stream_id}/delete", response_model=schemas.BaseResponse)
async def delete_live_stream(
    stream_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除直播(主播本人或管理员可删除)"""
    try:
        stream = db.query(models.LiveStream).filter(models.LiveStream.id == stream_id).first()
        if not stream:
            raise HTTPException(
                status_code=404,
                detail="直播不存在"
            )
        
        # 🔥 修改权限验证：允许主播本人或管理员操作
        user_role = getattr(current_user, 'role', 'user')
        if stream.user_id != current_user.id and user_role != 'admin':
            raise HTTPException(
                status_code=403,
                detail="无权限删除该直播"
            )
        
        db.delete(stream)
        db.commit()
        return {
            'code': 200,
            'message': '直播已删除'
        }
    except Exception as e:
        db.rollback()
        print(f"删除直播错误: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f'删除直播失败: {str(e)}'
        )

@router.post("/comment", response_model=schemas.LiveCommentResponse)
async def add_live_comment(
    comment_data: schemas.LiveCommentCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """发送直播评论 - 对应原Flask的 add_live_comment"""
    try:
        print("=== 发送直播评论 API 被调用 ===")
        
        print(f"🔍 评论参数: stream_id={comment_data.stream_id}, content={comment_data.content}")
        print(f"🎯 当前用户ID: {current_user.id}")
        
        # 创建评论
        comment = models.LiveComment(
            live_stream_id=comment_data.stream_id,  # 🔥 使用 live_stream_id
            user_id=current_user.id,
            content=comment_data.content
            # timestamp 会自动生成，不需要手动设置
        )
        
        db.add(comment)
        db.commit()
        db.refresh(comment)
        
        print(f"✅ 评论创建成功: 直播ID={comment_data.stream_id}, 用户ID={current_user.id}, 内容={comment_data.content}")
        
        return {
            'code': 200, 
            'message': '发送成功',
            'data': {
                'id': comment.id,
                'content': comment_data.content,
                'created_time': comment.timestamp.strftime('%H:%M') if comment.timestamp else datetime.datetime.now().strftime('%H:%M')
            }
        }
        
    except Exception as e:
        db.rollback()
        print(f"发送评论错误: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f'发送失败: {str(e)}'
        )

# 在 live.py 中修改 get_live_comments 函数
@router.get("/comments/{stream_id}", response_model=schemas.LiveCommentListResponse)
async def get_live_comments(
    stream_id: int,
    db: Session = Depends(get_db)
):
    """获取直播评论 - 修复时间显示"""
    try:
        print(f"=== 获取直播评论 API 被调用: stream_id={stream_id} ===")
        
        comments = db.query(models.LiveComment).filter(
            models.LiveComment.live_stream_id == stream_id
        ).order_by(models.LiveComment.timestamp.asc()).all()
        
        comment_list = []
        for comment in comments:
            user_name = comment.user.name if comment.user else '匿名用户'
            
            # 🔥 修复：UTC时间转北京时间
            display_time = "未知时间"
            if comment.timestamp:
                from datetime import timedelta
                beijing_time = comment.timestamp + timedelta(hours=8)
                display_time = beijing_time.strftime('%H:%M')
            
            comment_list.append({
                'id': comment.id,
                'username': user_name,
                'avatar': '/api/imgs/avatar-default.jpg',
                'content': comment.content,
                'time': display_time,  # 🔥 使用转换后的时间
                'isOwn': False,
                'isSystem': False
            })
        
        print(f"返回 {len(comment_list)} 条评论")
        return {
            'code': 200, 
            'data': comment_list, 
            'message': 'success'
        }
        
    except Exception as e:
        print(f"获取评论错误: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f'获取评论失败: {str(e)}'
        )
# ==================== 管理员专用接口 ====================

@router.get("/admin/streams", response_model=schemas.LiveStreamListResponse)
async def get_all_live_streams(
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    title: Optional[str] = Query(None),
    streamer: Optional[str] = Query(None),
    status: Optional[int] = Query(None),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """管理员获取所有直播流"""
    try:
        print("=== 管理员获取直播列表 API 被调用 ===")
        
        # 检查管理员权限
        user_role = getattr(current_user, 'role', 'user')
        if user_role != 'admin':
            raise HTTPException(
                status_code=403,
                detail="需要管理员权限"
            )
        
        # 计算偏移量
        offset = (page - 1) * pageSize
        
        # 构建查询
        query = db.query(models.LiveStream)
        
        # 应用筛选条件
        if title:
            query = query.filter(models.LiveStream.title.contains(title))
        if status is not None:
            query = query.filter(models.LiveStream.status == status)
        if streamer:
            query = query.join(models.User).filter(models.User.name.contains(streamer))
        
        # 获取总数
        total = query.count()
        
        # 获取分页数据
        streams = query.offset(offset).limit(pageSize).all()
        
        print(f"管理员获取到 {len(streams)} 个直播流")
        
        # 构建响应数据
        stream_list = []
        for stream in streams:
            # 获取评论数量
            comment_count = db.query(models.LiveComment).filter(
                models.LiveComment.live_stream_id == stream.id
            ).count()
            
            # 获取主播名称
            streamer_name = '未知主播'
            if stream.user:
                streamer_name = stream.user.name
            
            stream_data = {
                "id": stream.id,
                "stream_id": stream.id,
                "title": stream.title,
                "description": stream.description or "",
                "cover": stream.cover_image or "/api/imgs/live-default.svg",
                "category": "live",
                "status": stream.status,
                "status_text": "直播中" if stream.status == 1 else "已结束",
                "viewer_count": stream.viewer_count or 0,
                "max_viewers": stream.max_viewers or 0,
                "streamer": streamer_name,
                "streamer_id": stream.user_id,
                "avatar": "/api/imgs/avatar-default.jpg",
                "likes": 0,
                "chat_count": comment_count,
                "comment_count": comment_count,
                "stream_key": stream.stream_key,
                "created_time": stream.created_time.isoformat() if stream.created_time else None,
                "start_time": stream.start_time.isoformat() if stream.start_time else None,
                "end_time": stream.end_time.isoformat() if stream.end_time else None
            }
            stream_list.append(stream_data)
        
        return {
            "code": 200,
            "message": "获取直播列表成功",
            "data": stream_list,
            "pagination": {
                "page": page,
                "pageSize": pageSize,
                "total": total,
                "hasMore": len(stream_list) == pageSize
            }
        }
        
    except Exception as e:
        print(f"管理员获取直播列表错误: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"获取直播列表失败: {str(e)}")

@router.post("/admin/stream/{stream_id}/status", response_model=schemas.BaseResponse)
async def admin_update_stream_status(
    stream_id: int,
    status_data: dict,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """管理员更新直播状态"""
    try:
        print(f"=== 管理员更新直播状态 API 被调用: stream_id={stream_id} ===")
        print(f"🔍 当前用户ID: {current_user.id}, 角色: {getattr(current_user, 'role', 'user')}")
        
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
            'message': f'直播状态已更新'
        }
        
    except Exception as e:
        db.rollback()
        print(f"管理员更新直播状态错误: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f'更新直播状态失败: {str(e)}'
        )

@router.delete("/admin/stream/{stream_id}", response_model=schemas.BaseResponse)
async def admin_delete_live_stream(
    stream_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """管理员删除直播"""
    try:
        print(f"=== 管理员删除直播 API 被调用: stream_id={stream_id} ===")
        
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
        
        # 删除相关评论
        db.query(models.LiveComment).filter(
            models.LiveComment.live_stream_id == stream_id
        ).delete()
        
        # 删除直播
        db.delete(stream)
        db.commit()
        
        print(f"✅ 管理员 {current_user.name} 删除了直播: {stream.title}")
        
        return {
            'code': 200,
            'message': '直播已删除'
        }
        
    except Exception as e:
        db.rollback()
        print(f"管理员删除直播错误: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f'删除直播失败: {str(e)}'
        )