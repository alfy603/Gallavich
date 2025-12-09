from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import models, schemas
from app.security import get_current_user 
import datetime  # 🔥 确保导入 datetime

router = APIRouter(prefix="/comments", tags=["comments"])  # 🔥 添加正确的 prefix

@router.get("/show/{vod_id}", response_model=schemas.CommentListResponse)
async def show_comments(vod_id: int, db: Session = Depends(get_db)):
    """
    展示评论信息
    """
    def get_all_replies(reply_comments, result: List):
        for comment in reply_comments:
            # 🔥 方案A插入点1：修复回复时间显示
            time_str = "未知时间"
            if comment.timestamp:
                from datetime import timedelta
                beijing_time = comment.timestamp + timedelta(hours=8)  # 🔥 UTC转北京时间
                time_str = beijing_time.strftime('%Y-%m-%d %H:%M:%S')
            
            reply = {
                "user_name": comment.user.name,
                "id": comment.id,
                "reply_user_name": comment.replied.user.name if comment.replied else None,
                "body": comment.body,
                "time": time_str,  # 🔥 使用转换后的时间
                "user_id": comment.user_id,
            }
            result.append(reply)
            if comment.replies:
                get_all_replies(comment.replies, result)

    comments = db.query(models.Comment).filter(
        models.Comment.movdetail_id == vod_id
    ).order_by(models.Comment.timestamp.desc()).all()
    
    comment_list = []
    for comment in comments:
        # 🔥 方案A插入点2：修复主评论时间显示
        time_str = "未知时间"
        if comment.timestamp:
            from datetime import timedelta
            beijing_time = comment.timestamp + timedelta(hours=8)  # 🔥 UTC转北京时间
            time_str = beijing_time.strftime('%Y-%m-%d %H:%M:%S')
            print(f"    ✅ UTC时间: {comment.timestamp}, 北京时间: {beijing_time}")
        
        c = {
            "user_name": comment.user.name,
            "body": comment.body,
            "time": time_str,  # 🔥 使用转换后的时间
            "id": comment.id,
            "user_id": comment.user_id,
        }
        reply_list = []
        if comment.replies:
            get_all_replies(comment.replies, reply_list)
        c['reply_list'] = reply_list
        comment_list.append(c)
    
    return {
        "code": 200,
        "data": comment_list,
        "message": "评论获取成功"
    }
    
# 在 comments.py 中修改 post_comments 函数
@router.post("/publish/{vod_id}")
async def post_comments(
    vod_id: int, 
    comment_data: schemas.CommentCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    发表评论 - 手动设置时间戳
    """
    if not comment_data.body:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请输入评论内容"
        )
    
    try:
        # 🔥 修复：手动设置时间戳为当前时间
        comment = models.Comment(
            body=comment_data.body,
            user_id=current_user.id,
            movdetail_id=vod_id,
            timestamp=datetime.datetime.utcnow()  # 🔥 手动设置时间
        )
        db.add(comment)
        db.commit()
        db.refresh(comment)
        
        print(f"✅ 新评论发表成功: 用户={current_user.name}, 时间={comment.timestamp}")
        
        return {
            "code": 200,
            "message": "评论发布成功"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"评论发布失败: {str(e)}"
        )

# 在 comments.py 中修改 reply_comment 函数
@router.post("/reply/{comment_id}")
async def reply_comment(
    comment_id: int,
    reply_data: schemas.CommentCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    回复评论 - 手动设置时间戳
    """
    parent_comment = db.query(models.Comment).filter(
        models.Comment.id == comment_id
    ).first()
    
    if not parent_comment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="此评论已不存在"
        )
    
    if not reply_data.body:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请输入回复内容"
        )
    
    try:
        # 🔥 修复：手动设置时间戳为当前时间
        reply_comment = models.Comment(
            body=reply_data.body,
            user_id=current_user.id,
            replied_id=comment_id,
            movdetail_id=parent_comment.movdetail_id,
            timestamp=datetime.datetime.utcnow()  # 🔥 手动设置时间
        )
        db.add(reply_comment)
        db.commit()
        db.refresh(reply_comment)
        
        print(f"✅ 回复发表成功: 用户={current_user.name}, 时间={reply_comment.timestamp}")
        
        return {
            "code": 200,
            "message": "评论回复成功"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"回复失败: {str(e)}"
        )
        
@router.delete("/comment/{comment_id}")
async def delete_comment(
    comment_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 删除评论逻辑
    comment = db.query(models.Comment).filter(
        models.Comment.id == comment_id,
        models.Comment.user_id == current_user.id
    ).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评论不存在或无权限删除"
        )
    db.delete(comment)
    db.commit()
    return {
        "code": 200,
        "message": "评论删除成功"
    }

@router.delete("/reply/{reply_id}")
async def delete_reply(
    reply_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 删除回复逻辑
    reply = db.query(models.Comment).filter(
        models.Comment.id == reply_id,
        models.Comment.user_id == current_user.id
    ).first()
    if not reply:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="回复不存在或无权限删除"
        )
    db.delete(reply)
    db.commit()
    return {
        "code": 200,
        "message": "回复删除成功"
    }

    # 删除回复逻辑