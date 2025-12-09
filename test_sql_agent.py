"""测试 SQL Agent"""
import os
from dotenv import load_dotenv
from app.agents.sql_agent import SQLAgent

# 加载环境变量
load_dotenv()

def test_search(question: str):
    print(f"\n{'='*60}")
    print(f"🔍 测试问题: {question}")
    print(f"{'='*60}\n")
    
    agent = SQLAgent()
    result = agent.search(question)
    
    print(f"\n✅ 搜索完成")
    print(f"成功: {result['success']}")
    print(f"最终SQL: {result['final_sql']}")
    print(f"数据条数: {len(result['data'])}")
    print(f"解释: {result.get('explanation', 'N/A')}")
    print(f"反思: {result.get('reflection', 'N/A')}")
    
    if result.get('error'):
        print(f"❌ 错误: {result['error']}")
    
    if result['data']:
        print(f"\n前3条数据:")
        for i, item in enumerate(result['data'][:3], 1):
            print(f"{i}. {item}")

if __name__ == "__main__":
    # 测试几个问题
    test_search("评论最多的电影")
    test_search("最近更新的动漫有哪些？")
    test_search("2024年的韩剧")
