import requests
import pymysql
import time

def sync_videos_correct_field():
    """使用正确的 vod_id 字段进行同步"""
    
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '123456',
        'database': 'movie', 
        'charset': 'utf8mb4'
    }
    
    base_api = "https://m3u8.apiyhzy.com/api.php/provide/vod/"
    
    print("🎬 开始同步视频数据（正确字段版）...")
    print("🔄 使用 vod_id 字段作为主键")
    
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            # 先清理数据
            print("🗑️ 清理数据...")
            cursor.execute("DELETE FROM sakura_comment")
            cursor.execute("DELETE FROM sakura_movdetail")
            connection.commit()
            print("✅ 数据清理完成")
            
            total_synced = 0
            
            # 同步数据
            for page in range(2, 21):
                print(f"\n📄 同步第 {page} 页...")
                
                url = f"{base_api}?ac=detail&pg={page}"
                response = requests.get(url, timeout=10)
                data = response.json()
                
                videos = data.get('list', [])
                print(f"✅ 获取到 {len(videos)} 个视频")
                
                for video in videos:
                    try:
                        # 🎯 关键：使用 vod_id 字段，不指定 id 字段
                        insert_sql = """
                        INSERT INTO sakura_movdetail 
                        (vod_id, vod_name, vod_pic, vod_remarks, type_id, type_name, 
                         vod_content, vod_play_url, vod_time)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                        """
                        
                        cursor.execute(insert_sql, (
                            video.get('vod_id'),        # 使用 API 返回的 vod_id
                            video.get('vod_name'),
                            video.get('vod_pic'), 
                            video.get('vod_remarks'),
                            video.get('type_id'),
                            video.get('type_name'),
                            video.get('vod_content'),
                            video.get('vod_play_url')
                        ))
                        
                        total_synced += 1
                        vod_name = video.get('vod_name', '未知视频')
                        print(f"   ✅ 新增: {vod_name[:25]}... (vod_id: {video.get('vod_id')})")
                        
                    except Exception as e:
                        print(f"❌ 插入视频失败 {video.get('vod_id')}: {e}")
                        continue
                
                connection.commit()
                print(f"💾 第 {page} 页完成")
                time.sleep(1)
            
            print(f"\n🎉 同步完成！")
            print(f"📊 总共新增: {total_synced} 个真实视频")
            
            # 显示统计
            cursor.execute("SELECT COUNT(*) FROM sakura_movdetail")
            total_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT type_name, COUNT(*) FROM sakura_movdetail GROUP BY type_name")
            type_stats = cursor.fetchall()
            
            cursor.execute("SELECT vod_name, vod_id FROM sakura_movdetail ORDER BY vod_id DESC LIMIT 5")
            latest = cursor.fetchall()
            
            print(f"\n📈 数据库统计:")
            print(f"   视频总数: {total_count}")
            print(f"\n🎭 分类分布:")
            for type_name, count in type_stats:
                print(f"   {type_name}: {count} 个视频")
            
            print(f"\n🆕 最新视频:")
            for i, video in enumerate(latest, 1):
                print(f"   {i}. {video[0]} (vod_id: {video[1]})")
                
    except Exception as e:
        connection.rollback()
        print(f"❌ 同步失败: {e}")
    finally:
        connection.close()

if __name__ == "__main__":
    sync_videos_correct_field()