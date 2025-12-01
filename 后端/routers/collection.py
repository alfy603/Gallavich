from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import models, schemas
from app.security import get_current_user 

router = APIRouter(prefix="/collection", tags=["video-collection"])

@router.get("/show", response_model=schemas.CollectionListResponse)
async def show_collect_video(
    page: int = Query(1, ge=1, description="页码"),
    per_page: int = Query(12, ge=1, le=100, description="每页数量"),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    返回该用户的所有收藏视频 - 对应原Flask的 show_collect_video
    """
    print(f"=== 认证调试 ===")
    print(f"当前用户ID: {current_user.id}")
    
    user_id = current_user.id
    
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="用户未登录或用户ID无效"
        )
    
    # 查询用户收藏
    user_collection = db.query(models.UserCollection).filter(
        models.UserCollection.user_id == user_id
    ).first()
    
    collect_vod_list = []
    has_more = False
    
    if user_collection and user_collection.movdetail_id_list:
        # 解析电影ID列表
        store_vod_list = user_collection.movdetail_id_list.strip(';').split(';')
        store_vod_list = [id_str for id_str in store_vod_list if id_str]
        
        print(f"用户 {user_id} 的收藏电影ID列表: {store_vod_list}")
        print(f"收藏电影数量: {len(store_vod_list)}")
        
        if store_vod_list:
            try:
                # 将字符串ID转换为整数
                vod_ids = [int(vod_id) for vod_id in store_vod_list if vod_id.isdigit()]
                print(f"转换后的整数ID列表: {vod_ids}")
                
                # 分页计算
                start_index = (page - 1) * per_page
                end_index = start_index + per_page
                page_vod_ids = vod_ids[start_index:end_index]
                
                print(f"当前页ID范围: {start_index} - {end_index}")
                print(f"当前页查询的ID: {page_vod_ids}")
                
                if page_vod_ids:
                    # 查询电影详情
                    collect_movs = db.query(models.MovDetail).filter(
                        models.MovDetail.id.in_(page_vod_ids)
                    ).order_by(models.MovDetail.vod_time.desc()).all()
                    
                    print(f"查询到的电影数量: {len(collect_movs)}")
                    
                    for mov in collect_movs:
                        collect_vod_list.append({
                            'vod_id': mov.id,
                            'vod_pic': mov.vod_pic,
                            'vod_name': mov.vod_name, 
                            'vod_remarks': mov.vod_remarks,
                            'type_name': mov.type_name
                        })
                
                # 计算总页数
                total_pages = (len(vod_ids) + per_page - 1) // per_page
                has_more = page < total_pages
                
            except Exception as e:
                print(f"查询收藏视频时出错: {e}")
                raise HTTPException(
                    status_code=500,
                    detail="查询收藏列表失败"
                )
    
    print(f"返回的收藏视频数量: {len(collect_vod_list)}")
    
    return {
        'code': 200,
        'message': '收藏的视频信息',
        'data': {
            'collections': collect_vod_list,
            'pagination': {
                'current_page': page,
                'per_page': per_page,
                'total': len(store_vod_list) if user_collection else 0,
                'has_more': has_more
            }
        }
    }

@router.get("/is_collection", response_model=schemas.IsCollectionResponse)
async def show_is_collect_video(
    vod_id: int = Query(..., description="视频ID"),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    返回该视频是否被收藏 - 对应原Flask的 show_is_collect_video
    """
    user_collection = db.query(models.UserCollection).filter(
        models.UserCollection.user_id == current_user.id
    ).first()
    
    if user_collection:
        vod_id_str = str(vod_id)
        if vod_id_str in user_collection.movdetail_id_list:
            return {
                'code': 200,
                'message': '该视频已被收藏',
                'data': 1
            }
    
    return {
        'code': 200,
        'message': '该视频未被收藏',
        'data': 0
    }

@router.post("/add", response_model=schemas.BaseResponse)
async def add_collect_video(
    collection_data: schemas.CollectionCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    添加收藏视频 - 对应原Flask的 add_collect_video
    """
    vod_id = collection_data.vod_id
    print(f"添加收藏: user_id={current_user.id}, vod_id={vod_id}")
    
    user_collection = db.query(models.UserCollection).filter(
        models.UserCollection.user_id == current_user.id
    ).first()
    
    vod_id_str = str(vod_id)
    
    # 如果有收藏信息则更新，没有则添加
    if user_collection:
        # 检查是否已经收藏
        current_ids = user_collection.movdetail_id_list.strip(';')
        ids_list = current_ids.split(';') if current_ids else []
        
        if vod_id_str not in ids_list:
            ids_list.append(vod_id_str)
            user_collection.movdetail_id_list = ';'.join(ids_list) + ';'
            try:
                db.commit()
                print(f"更新收藏成功: {user_collection.movdetail_id_list}")
            except Exception as e:
                db.rollback()
                print(f"更新收藏失败: {e}")
                raise HTTPException(
                    status_code=500,
                    detail="收藏失败"
                )
        else:
            return {
                'code': 200,
                'message': '视频已收藏'
            }
    else:
        try:
            user_collection = models.UserCollection(
                user_id=current_user.id, 
                movdetail_id_list=vod_id_str + ';'
            )
            db.add(user_collection)
            db.commit()
            print(f"新增收藏成功: {user_collection.movdetail_id_list}")
        except Exception as e:
            db.rollback()
            print(f"新增收藏失败: {e}")
            raise HTTPException(
                status_code=500,
                detail="收藏失败"
            )
    
    return {
        'code': 200,
        'message': '视频收藏成功'
    }

@router.delete("/remove", response_model=schemas.BaseResponse)
async def remove_collect_video(
    collection_data: schemas.CollectionRemove,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除收藏视频 - 对应原Flask的 remove_collect_video
    """
    vod_id = collection_data.vod_id
    user_collection = db.query(models.UserCollection).filter(
        models.UserCollection.user_id == current_user.id
    ).first()
    
    if user_collection:
        try:
            vod_id_str = str(vod_id) + ';'
            user_collection.movdetail_id_list = user_collection.movdetail_id_list.replace(vod_id_str, '')
            db.commit()
            
            # 获取更新后的收藏列表
            store_vod_list = []
            if user_collection.movdetail_id_list:
                store_vod_list = list(set(user_collection.movdetail_id_list.strip(';').split(';')))
            
            return {
                'code': 200,
                'message': '视频删除收藏成功',
                'data': store_vod_list
            }
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"删除收藏失败: {str(e)}"
            )
    else:
        raise HTTPException(
            status_code=400,
            detail="没有要删除收藏的视频信息"
        )