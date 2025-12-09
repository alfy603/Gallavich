import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine
from app import models
from app.task.sakura_crawler import SakuraData

def batch_crawl_movies(batch_size=10):
    """
    分批爬取电影数据
    batch_size: 每次爬取的页数
    """
    # 创建数据库表
    models.Base.metadata.create_all(bind=engine)
    
    sk = SakuraData()
    
    print(f"🚀 开始分批爬取，每批 {batch_size} 页...")
    
    # 先爬取基本信息
    print("📋 爬取电影基本信息...")
    for page in range(1, batch_size + 1):
        sk.get_mov_info(page)
        print(f"✅ MovInfo 第 {page} 页完成")
    
    # 爬取详细信息
    print("🎬 爬取电影详细信息...")
    for page in range(1, batch_size + 1):
        sk.get_mov_detail(page)
        print(f"✅ MovDetail 第 {page} 页完成")
    
    print(f"🎉 第一批 {batch_size} 页数据爬取完成！")
    print("现在前端应该能看到电影数据了！")

if __name__ == '__main__':
    batch_crawl_movies(5)  # 先爬5页测试