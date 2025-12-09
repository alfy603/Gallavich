"""测试 DeepSeek API 连接"""
import os
from dotenv import load_dotenv
from openai import OpenAI

# 加载环境变量
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")

print(f"🔑 API Key: {api_key[:10]}...{api_key[-4:] if api_key else 'None'}")
print(f"🌐 Base URL: {base_url}")
print()

try:
    client = OpenAI(
        api_key=api_key,
        base_url=base_url
    )
    
    print("📡 测试 API 连接...")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "user", "content": "你好，请回复'连接成功'"}
        ],
        max_tokens=50
    )
    
    print("✅ API 连接成功!")
    print(f"📝 响应: {response.choices[0].message.content}")
    
except Exception as e:
    print(f"❌ API 连接失败: {e}")
    print("\n🔧 解决方案:")
    print("1. 检查 API key 是否正确且未过期")
    print("2. 访问 https://platform.deepseek.com/api_keys 重新生成 API key")
    print("3. 确认账户有足够余额")
    print("4. 确认 base_url 正确: https://api.deepseek.com/v1")
