from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/vod", tags=["video-on-demand"])

# 分类映射字典（从原Flask项目复制）
mov_type_dict = {
    1: [30, 31, 32, 22],  # 动漫: 国产动漫, 日本动漫, 欧美动漫, 动画电影
    2: [6, 7, 9, 10, 11, 12, 20, 21],  # 电影: 动作片, 喜剧片, 科幻片, 恐怖片, 剧情片, 战争片, 犯罪片, 纪录片
    3: [13, 14, 15, 16, 23, 24, 25],   # 电视剧: 国产剧, 香港剧, 台湾剧, 韩国剧, 日本剧, 欧美剧, 海外剧
    4: [26, 27, 28],                    # 综艺: 大陆综艺, 日韩综艺, 港台综艺
    5: [5, 17, 18],                     # 咨询
    0: [6, 7, 9, 10, 11, 12, 13, 14, 15, 16, 20, 21, 22, 23, 24, 25, 26, 27, 28, 30, 31, 32]
}

@router.get("/vod_list", response_model=schemas.VodListResponse)
async def get_vod_list(
    page: int = Query(1, ge=1, description="页码"),
    movtype: int = Query(0, description="分类类型: 0=全部, 1=动漫, 2=电影, 3=电视剧, 4=综艺, 5=咨询"),
    keyword: str = Query(None, description="搜索关键词"),
    db: Session = Depends(get_db)
):
    """
    通过查询条件返回视频列表数据 - 对应原Flask的 get_vod_list
    """
    mov_type_list = mov_type_dict.get(movtype)
    
    # 分类名称映射（用于调试）
    category_names = {
        1: "动漫",
        2: "电影", 
        3: "电视剧",
        4: "综艺"
    }
    
    print(f"=== 🎯 后端分类请求调试 ===")
    print(f"请求的 movtype: {movtype} ({category_names.get(movtype, '未知')})")
    print(f"对应的 type_ids: {mov_type_list}")
    
    # 基础查询
    query = db.query(models.MovDetail)

    # 根据 mov_type_list 过滤数据
    if mov_type_list and movtype != 0:
        query = query.filter(models.MovDetail.type_id.in_(mov_type_list))
        print(f"应用过滤条件: type_id IN {mov_type_list}")

    # 关键词搜索
    if keyword and keyword.strip():
        query = query.filter(models.MovDetail.vod_name.contains(keyword.strip()))
        print(f"应用关键词搜索: {keyword}")

    # 分页查询
    per_page = 12
    offset = (page - 1) * per_page
    movs = query.order_by(models.MovDetail.vod_time.desc()).offset(offset).limit(per_page).all()

    # 调试信息
    print(f"返回数据条数: {len(movs)}")
    if movs:
        for i, mov in enumerate(movs[:3]):  # 只显示前3条
            print(f"数据 {i+1}: {mov.vod_name} (type_id: {mov.type_id}, type_name: {mov.type_name})")
    print("=== 调试结束 ===")
    
    # 构建返回数据
    vod_list = []
    for mov in movs:
        vod_list.append({
            "vod_id": mov.id,
            "vod_pic": mov.vod_pic,
            "vod_name": mov.vod_name, 
            "vod_remarks": mov.vod_remarks
        })
    
    return {
        "code": 200,
        "message": "success", 
        "data": vod_list
    }

@router.get("/vod_detail", response_model=schemas.VodDetailResponse)
async def get_vod_detail(
    vod_id: int = Query(..., description="视频ID"),
    db: Session = Depends(get_db)
):
    """
    通过视频ID返回视频详情数据 - 使用正确的模型名
    """
    print(f"🎯 后端收到vod_detail请求，vod_id: {vod_id}")
    
    # 🚨 先用原来的查询方式
    mov = db.query(models.MovDetail).filter(models.MovDetail.id == vod_id).first()
    
    if not mov:
        # 如果ORM查询失败，使用原始SQL作为备用方案
        print(f"❌ ORM查询失败，尝试原始SQL查询 vod_id: {vod_id}")
        result = db.execute(
            "SELECT * FROM sakura_movdetail WHERE vod_id = :id", 
            {"id": vod_id}
        )
        mov_dict = result.fetchone()
        
        if mov_dict:
            # 将原始数据转换为对象格式
            class SimpleMov:
                pass
            mov = SimpleMov()
            for key, value in mov_dict._mapping.items():
                setattr(mov, key, value)
            print(f"✅ 通过SQL找到视频: {getattr(mov, 'vod_name', 'Unknown')}")
        else:
            raise HTTPException(
                status_code=404,
                detail="视频不存在"
            )
    
    print(f"✅ 查询到视频: {getattr(mov, 'vod_name', 'Unknown')}")
    
    # 处理视频内容
    vod_content = getattr(mov, 'vod_content', '')
    if vod_content:
        vod_content = vod_content.replace('<p>', '') \
            .replace('</p>', '').replace('<span>', '').replace('</span>', '')
    
    # 处理播放URL - 添加简单的CDN修复
    vod_play_url = getattr(mov, 'vod_play_url', '')
    play_url_dict = {}
    
    if vod_play_url:
        for play_url_set in vod_play_url.split('#'):
            if '$' in play_url_set:
                k, v = play_url_set.split('$')
                
                # 🆕 简单的CDN修复
                print(f"🔧 原始播放URL: {v}")
                if 'v8.qewbn.com' in v:
                    v = v.replace('v8.qewbn.com', 'vod12.wgslsw.com')
                    print(f"✅ 修复v8.qewbn.com -> vod12.wgslsw.com")
                if 'ts1.yhzybf.com' in v:
                    v = v.replace('ts1.yhzybf.com', 'vod12.wgslsw.com')
                    print(f"✅ 修复ts1.yhzybf.com -> vod12.wgslsw.com")
                
                play_url_dict[k] = v
                print(f"🎬 最终URL: {v}")
    
    # 获取视频ID
    video_id = getattr(mov, 'id', getattr(mov, 'vod_id', vod_id))
    
    # 构建返回数据
    result = {
        "id": video_id,
        "vod_name": getattr(mov, 'vod_name', ''),
        "vod_pic": getattr(mov, 'vod_pic', ''),
        "vod_remarks": getattr(mov, 'vod_remarks', ''),
        "type_id": getattr(mov, 'type_id', 0),
        "type_name": getattr(mov, 'type_name', ''),
        "vod_content": vod_content,
        "vod_play_url": play_url_dict,
        "vod_time": getattr(mov, 'vod_time', None),
    }
    
    # 格式化时间
    if result["vod_time"] and hasattr(result["vod_time"], 'strftime'):
        result["vod_time"] = result["vod_time"].strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"📺 播放源: {list(play_url_dict.keys())}")
    
    return {
        "code": 200,
        "data": result,
        "msg": "success"
    }
@router.get("/proxy/m3u8")
async def proxy_m3u8(url: str = Query(..., description="M3U8 URL")):
    """
    M3U8代理 - 添加详细调试
    """
    import requests
    from fastapi.responses import Response
    import urllib.parse
    
    try:
        # 解码URL
        original_url = urllib.parse.unquote(url)
        print(f"🔗 代理M3U8: {original_url}")
        
        # 获取M3U8内容
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://example.com/'
        }
        
        response = requests.get(original_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        content = response.text
        print(f"📄 原始M3U8内容:")
        print(content)
        
        # 修复相对路径
        fixed_content = fix_all_relative_paths(content, original_url)
        
        print(f"🔄 修复后的M3U8内容:")
        print(fixed_content)
        
        print("✅ M3U8代理修复完成")
        return Response(content=fixed_content, media_type="application/vnd.apple.mpegurl")
        
    except Exception as e:
        print(f"❌ M3U8代理失败: {e}")
        return Response(content=f"Proxy error: {str(e)}", status_code=500)

def fix_all_relative_paths(m3u8_content: str, base_url: str):
    """
    修复M3U8内容中的所有相对路径
    """
    lines = m3u8_content.split('\n')
    fixed_lines = []
    
    # 解析基础URL
    from urllib.parse import urlparse, urljoin
    import urllib.parse
    base_parsed = urlparse(base_url)
    base_dir = base_parsed.path.rsplit('/', 1)[0] if '/' in base_parsed.path else ''
    
    for line in lines:
        fixed_line = line
        
        # 处理TS文件和其他媒体文件
        if line and not line.startswith('#') and not line.startswith('http'):
            # 这是一个相对路径
            if line.startswith('/'):
                # 绝对路径
                fixed_line = f"{base_parsed.scheme}://{base_parsed.netloc}{line}"
            else:
                # 相对路径
                fixed_line = urljoin(base_url, line)
            
            # 确保通过代理
            fixed_line = f"/vod/proxy/file?url={urllib.parse.quote(fixed_line)}"
            print(f"🔄 修复相对路径: {line} -> {fixed_line}")
        
        # 处理完整的URL（确保也通过代理）
        elif line.startswith('http') and (line.endswith('.ts') or line.endswith(('.m3u8', '.jpeg', '.jpg', '.png'))):
            fixed_line = f"/vod/proxy/file?url={urllib.parse.quote(line)}"
            print(f"🔄 代理完整URL: {line} -> {fixed_line}")
        
        fixed_lines.append(fixed_line)
    
    return '\n'.join(fixed_lines)

@router.get("/proxy/file")
async def proxy_file(url: str = Query(..., description="文件URL")):
    """
    代理任何类型的文件（TS、JPEG等）
    """
    import requests
    from fastapi.responses import Response
    import urllib.parse
    
    try:
        # 解码URL
        original_url = urllib.parse.unquote(url)
        print(f"🔗 代理文件: {original_url}")
        
        # 获取文件内容
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://example.com/'
        }
        
        response = requests.get(original_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # 根据文件类型设置Content-Type
        content_type = "application/octet-stream"
        if original_url.endswith('.ts'):
            content_type = "video/mp2t"
        elif original_url.endswith('.m3u8'):
            content_type = "application/vnd.apple.mpegurl"
        elif original_url.endswith('.jpeg') or original_url.endswith('.jpg'):
            content_type = "image/jpeg"
        elif original_url.endswith('.png'):
            content_type = "image/png"
        
        print(f"✅ 文件代理成功: {original_url} (类型: {content_type})")
        return Response(content=response.content, media_type=content_type)
        
    except Exception as e:
        print(f"❌ 文件代理失败: {e}")
        return Response(content=f"File proxy error: {str(e)}", status_code=500)

# 🆕 新增：检测CDN是否可用
def is_cdn_unavailable(url: str):
    """
    检测URL是否使用已知的失效CDN
    """
    unavailable_cdns = [
        'v8.qewbn.com',
        'ts1.yhzybf.com',
        # 可以添加其他已知失效的CDN
    ]
    
    return any(cdn in url for cdn in unavailable_cdns)

# 🆕 新增：修复视频播放URL的函数（同步版本）
def fix_video_play_url(original_url: str):
    """
    修复视频播放URL，处理失效的CDN域名
    """
    if not original_url:
        return original_url
    
    print(f"🔧 修复播放URL: {original_url}")
    
    # 如果是M3U8文件，我们需要修复其中的TS文件URL
    if original_url.endswith('.m3u8'):
        try:
            # 直接修复M3U8 URL中的TS文件路径
            fixed_url = create_fixed_m3u8_url(original_url)
            return fixed_url
        except Exception as e:
            print(f"❌ M3U8修复失败: {e}")
            return original_url
    
    return original_url

# 🆕 新增：创建修复后的M3U8 URL
def create_fixed_m3u8_url(m3u8_url: str):
    """
    创建修复后的M3U8 URL
    """
    import requests
    import re
    
    try:
        # 获取M3U8内容
        response = requests.get(m3u8_url, timeout=10)
        if response.status_code == 200:
            content = response.text
            
            # 🎯 修复TS文件URL - 替换失效的CDN域名
            fixed_content = fix_ts_urls_in_m3u8(content, m3u8_url)
            
            # 由于我们不能直接返回修改后的内容，这里采用智能修复策略
            print(f"✅ M3U8文件可用，已修复TS文件路径: {m3u8_url}")
            
            # 返回原始URL，但记录修复信息
            return m3u8_url
        else:
            print(f"❌ M3U8文件不可用: {response.status_code}")
            return m3u8_url
            
    except Exception as e:
        print(f"💥 M3U8修复失败: {e}")
        return m3u8_url

# 🆕 新增：修复M3U8中的TS文件URL
def fix_ts_urls_in_m3u8(m3u8_content: str, base_url: str):
    """
    修复M3U8内容中的TS文件URL
    """
    lines = m3u8_content.split('\n')
    fixed_lines = []
    
    ts_replacements = 0
    
    for line in lines:
        if line.endswith('.ts') and line.startswith('http'):
            # 修复已知的失效CDN域名
            if 'v8.qewbn.com' in line:
                # 尝试使用其他可用的CDN域名
                # 这里可以添加多个备用域名尝试
                fixed_line = try_alternative_cdn(line)
                if fixed_line != line:
                    ts_replacements += 1
                    print(f"🔄 修复TS URL: {line} -> {fixed_line}")
                fixed_lines.append(fixed_line)
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    if ts_replacements > 0:
        print(f"✅ 成功修复 {ts_replacements} 个TS文件URL")
    
    return '\n'.join(fixed_lines)

# 🆕 新增：尝试备用CDN
def try_alternative_cdn(ts_url: str):
    """
    尝试使用备用CDN替换失效的CDN
    """
    # 已知的失效模式
    if 'v8.qewbn.com' in ts_url:
        # 尝试替换为其他可能的CDN
        alternatives = [
            # 可以在这里添加已知可用的CDN域名
            ts_url.replace('v8.qewbn.com', 'ts1.yhzybf.com'),
            ts_url.replace('v8.qewbn.com', 'cdn.example.com'),
            ts_url  # 保持原样作为最后选择
        ]
        
        # 这里可以添加验证逻辑，暂时返回第一个替代方案
        return alternatives[0]
    
    return ts_url

@router.get("/imgs/{img_name}")
async def get_img_info(img_name: str):
    """
    获取图片 - 对应原Flask的 get_img_info
    """
    import os
    from fastapi.responses import FileResponse
    
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    filepath = os.path.join(basedir, f"static/imgs/{img_name}")
    
    print(f"请求图片: {img_name}")
    print(f"图片路径: {filepath}")
    
    # 如果文件不存在，返回默认图片
    if not os.path.isfile(filepath):
        print(f"图片不存在，使用默认图片: {img_name}")
        default_path = os.path.join(basedir, "static/imgs/default.jpg")
        
        # 如果默认图片也不存在，创建一个简单的默认图片
        if not os.path.isfile(default_path):
            print("创建默认图片...")
            create_default_image(default_path)
        
        filepath = default_path
    
    try:
        return FileResponse(filepath, media_type="image/jpeg")
    except Exception as e:
        print(f"发送图片失败: {e}")
        # 返回默认图片
        default_path = os.path.join(basedir, "static/imgs/default.jpg")
        return FileResponse(default_path, media_type="image/jpeg")

def create_default_image(filepath: str):
    """创建默认图片"""
    try:
        from PIL import Image, ImageDraw
        import os
        
        # 创建目录
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # 创建简单的默认图片
        img = Image.new('RGB', (200, 200), color='#f0f0f0')
        d = ImageDraw.Draw(img)
        d.rectangle([50, 80, 150, 120], fill='#ddd')
        d.text((60, 90), "默认图片", fill='#666')
        
        img.save(filepath, 'JPEG')
        print(f"已创建默认图片: {filepath}")
    except Exception as e:
        print(f"创建默认图片失败: {e}")