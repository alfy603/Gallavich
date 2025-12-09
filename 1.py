import pymysql

db = pymysql.connect(
    host='localhost',
    user='root', 
    password='123456',
    database='movie'
)

cursor = db.cursor()

# 只找一个有问题的视频测试
cursor.execute("""
SELECT vod_id, vod_name, vod_play_url 
FROM sakura_movdetail 
WHERE vod_play_url LIKE '%v8.qewbn.com%' 
LIMIT 1
""")

test_video = cursor.fetchone()
if test_video:
    print("测试视频信息：")
    print(f"ID: {test_video[0]}")
    print(f"名称: {test_video[1]}")
    print(f"原始URL: {test_video[2]}")
    
    # 只修复这一个视频
    fixed_url = test_video[2].replace('v8.qewbn.com', 'vod12.wgslsw.com')
    
    print(f"修复后URL: {fixed_url}")
    
    # 更新这一个视频
    cursor.execute("""
    UPDATE sakura_movdetail 
    SET vod_play_url = %s 
    WHERE vod_id = %s
    """, (fixed_url, test_video[0]))
    
    db.commit()
    print(f"✅ 已修复测试视频: {test_video[1]}")
    
    # 记住这个视频ID，方便测试
    print(f"📝 测试视频ID: {test_video[0]}")

cursor.close()
db.close()