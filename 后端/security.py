from datetime import datetime, timedelta
from typing import Optional
import jwt  # 改为使用 PyJWT
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app import models

# JWT 配置
SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 密码加密上下文 - 添加更多支持的算法
pwd_context = CryptContext(
    schemes=["bcrypt", "pbkdf2_sha256"],  # 添加 pbkdf2_sha256 支持
    deprecated="auto"
)

# HTTP Bearer 认证
security = HTTPBearer()

def verify_password(plain_password, hashed_password):
    """验证密码 - 支持多种哈希格式，处理密码长度限制"""
    try:
        print(f"🔐 验证密码: plain='{plain_password}' (长度: {len(plain_password)}), hashed={hashed_password[:50]}...")
        
        # 如果哈希值为空或None，直接返回False
        if not hashed_password:
            print("❌ 哈希值为空")
            return False
        
        # 🔥 修复：处理密码长度限制
        # bcrypt 限制密码不能超过 72 字节
        password_bytes = plain_password.encode('utf-8')
        if len(password_bytes) > 72:
            print(f"⚠️ 密码字节长度 {len(password_bytes)} > 72，进行截断")
            # 截断到 72 字节
            truncated_bytes = password_bytes[:72]
            # 尝试用截断后的密码验证
            plain_password = truncated_bytes.decode('utf-8', errors='ignore')
            print(f"✅ 密码已截断为 {len(plain_password)} 字符")
            
        # 1. 首先尝试 bcrypt 格式 ($2b$, $2a$, $2y$)
        if hashed_password.startswith(('$2b$', '$2a$', '$2y$')):
            print("🎯 检测到 bcrypt 格式，使用 bcrypt 验证")
            try:
                # 使用 passlib 的 bcrypt 验证
                result = pwd_context.verify(plain_password, hashed_password)
                print(f"✅ bcrypt 验证结果: {result}")
                return result
            except Exception as e:
                print(f"❌ bcrypt 验证失败: {e}")
                return False
        
        # 2. 处理 pbkdf2_sha256 格式 - 🔥 修复格式检测
        elif hashed_password.startswith('$pbkdf2-sha256$'):
            print("🎯 检测到 pbkdf2-sha256 格式，使用专门验证")
            try:
                from passlib.hash import pbkdf2_sha256
                result = pbkdf2_sha256.verify(plain_password, hashed_password)
                print(f"✅ pbkdf2_sha256 验证结果: {result}")
                return result
            except Exception as e:
                print(f"❌ pbkdf2_sha256 验证失败: {e}")
                return False
                
        # 3. 其他格式使用默认验证
        else:
            print(f"⚠️ 使用默认验证: {hashed_password[:20]}...")
            try:
                result = pwd_context.verify(plain_password, hashed_password)
                print(f"✅ 默认验证结果: {result}")
                return result
            except Exception as e:
                print(f"❌ 默认验证失败: {e}")
                return False
                
    except Exception as e:
        print(f"❌ 密码验证异常: {e}")
        return False

def get_password_hash(password):
    """生成密码哈希 - 使用 pbkdf2_sha256"""
    try:
        # 使用 pbkdf2_sha256 生成哈希
        from passlib.hash import pbkdf2_sha256
        hashed = pbkdf2_sha256.hash(password)
        print(f"🔐 生成密码哈希 (pbkdf2_sha256): {hashed[:50]}...")
        return hashed
    except Exception as e:
        print(f"❌ 生成密码哈希失败: {e}")
        # 降级方案：使用 bcrypt
        hashed = pwd_context.hash(password)
        print(f"🔐 降级到 bcrypt 哈希: {hashed[:20]}...")
        return hashed
        
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    """验证令牌"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        return None

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """获取当前用户 - 添加状态检查"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        
        # 如果 token 以 "jwt " 开头，去掉前缀
        if token.startswith("jwt "):
            token = token[4:]
        
        payload = verify_token(token)
        if payload is None:
            raise credentials_exception
        
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        user = db.query(models.User).filter(models.User.name == username).first()
        if user is None:
            raise credentials_exception
        
        # 🔥 新增：检查用户是否被禁用
        if not user.is_active:
            print(f"❌ 用户已被禁用: {user.name}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="账户已被禁用"
            )
        
        return user
    except Exception as e:
        print(f"认证错误: {e}")
        raise credentials_exception

# 兼容原 Flask 项目的工具函数
def generate_auth_token(user_id: int, name: str, effective_time: int = 30):
    """生成 JWT token"""
    expire = datetime.utcnow() + timedelta(minutes=effective_time)
    to_encode = {
        "sub": name,
        "id": user_id,
        "name": name,
        "exp": expire
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def parse_user_from_token(token: str):
    """从 token 解析用户信息"""
    if token.startswith("jwt "):
        token = token[4:]
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {
            "id": payload.get("id"),
            "name": payload.get("name"),
            "sub": payload.get("sub")
        }
    except jwt.InvalidTokenError:
        return None
    
    
# 在 security.py 中添加管理员验证
def get_current_admin(current_user: models.User = Depends(get_current_user)):
    """验证当前用户是否为管理员"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有管理员权限"
        )
    return current_user