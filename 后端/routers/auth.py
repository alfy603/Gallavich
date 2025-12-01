from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app import models
from app import crud, schemas, security
from app.database import get_db  # 使用统一的 get_db

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

@router.post("/register")
async def register(request: Request, db: Session = Depends(get_db)):
    """
    用户注册 - 调试版本
    """
    try:
        # 查看原始请求数据
        body = await request.body()
        print(f"🔍 注册 - 原始请求数据: {body}")
        
        # 查看表单数据
        form_data = await request.form()
        print(f"🔍 注册 - 表单数据: {dict(form_data)}")
        
        # 尝试解析 JSON
        try:
            json_data = await request.json()
            print(f"🔍 注册 - JSON数据: {json_data}")
        except:
            print("🔍 注册 - 不是JSON数据")
        
        # 获取用户名和密码
        if form_data:
            username = form_data.get("username")
            password = form_data.get("password")
        else:
            # 如果是 JSON
            username = json_data.get("username")
            password = json_data.get("password")
        
        print(f"🔍 注册 - 解析出的数据 - 用户名: {username}, 密码长度: {len(password) if password else 0}")
        
        if not username or not password:
            return {
                "code": 400,
                "message": "用户名或密码不能为空",
                "data": None
            }
        
        # 检查用户是否存在
        db_user = db.query(models.User).filter(models.User.name == username).first()
        if db_user:
            return {
                "code": 400,
                "message": "注册失败, 当前用户名已被注册, 请更换用户名",
                "data": None
            }
        
        # 创建用户
        safe_password = password
        if len(safe_password) > 50:
            safe_password = safe_password[:50]
            
        new_user = models.User(
            name=username,
            password_hash=security.get_password_hash(safe_password)
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return {
            "code": 200,
            "message": "注册成功, 请重新登录",
            "data": None
        }
            
    except Exception as e:
        db.rollback()
        print(f"💥 注册异常: {e}")
        return {
            "code": 500,
            "message": f"注册失败: {str(e)}",
            "data": None
        }

@router.post("/login")
async def login(request: Request, db: Session = Depends(get_db)):
    """
    用户登录 - 添加用户状态检查
    """
    print("🎯 ========== 登录请求开始 ==========")
    
    try:
        # 查看原始请求数据
        body = await request.body()
        print(f"🔍 原始请求数据: {body}")
        
        # 查看表单数据
        form_data = await request.form()
        print(f"🔍 表单数据: {dict(form_data)}")
        
        # 尝试解析 JSON
        try:
            json_data = await request.json()
            print(f"🔍 JSON数据: {json_data}")
        except:
            print("🔍 不是JSON数据")
        
        # 获取用户名和密码
        if form_data:
            username = form_data.get("username")
            password = form_data.get("password")
        else:
            # 如果是 JSON
            username = json_data.get("username")
            password = json_data.get("password")
        
        print(f"🔍 解析出的数据 - 用户名: '{username}', 密码长度: {len(password) if password else 0}")
        
        if not username or not password:
            return {
                "code": 400,
                "message": "用户名或密码不能为空",
                "data": None
            }
        
        # 查找用户
        print(f"🔍 开始查找用户: '{username}'")
        user = db.query(models.User).filter(models.User.name == username).first()
        
        if not user:
            print(f"❌ 用户不存在: '{username}'")
            return {
                "code": 400,
                "message": "登录失败, 账户或密码不正确",
                "data": None
            }
        
        print(f"✅ 找到用户: ID={user.id}, Name='{user.name}'")
        print(f"🔑 用户状态: is_active={user.is_active}, role={user.role}")
        
        # � 新增：检查用户是否被禁用
        if not user.is_active:
            print(f"❌ 用户已被禁用: {user.name}")
            return {
                "code": 400,
                "message": "账户已被禁用，请联系管理员",
                "data": None
            }
        
        print(f"🔑 数据库中的密码哈希: {user.password_hash}")
        
        # 验证密码
        print("� 开始密码验证...")
        from app.security import verify_password
        is_valid = verify_password(password, user.password_hash)
        print(f"� 密码验证最终结果: {is_valid}")
        
        if is_valid:
            from app.security import generate_auth_token
            token = generate_auth_token(user_id=user.id, name=user.name)
            
            print(f"✅ 登录成功，生成token")
            
            return {
                "code": 200,
                "message": "Login successfully",
                "data": {
                    "token": "jwt " + token,
                    "user_id": user.id,
                    "username": user.name,
                    "role": getattr(user, 'role', 'user')
                }
            }
        else:
            print(f"❌ 密码验证失败")
            return {
                "code": 400,
                "message": "登录失败, 账户或密码不正确", 
                "data": None
            }
            
    except Exception as e:
        print(f"💥 登录异常: {e}")
        import traceback
        traceback.print_exc()
        return {
            "code": 500,
            "message": f"登录失败: {str(e)}",
            "data": None
        }
@router.get("/user", response_model=schemas.BaseResponse)
def get_user(current_user: models.User = Depends(security.get_current_user)):
    """
    获取当前用户信息
    """
    return {
        "code": 200,
        "message": "获取用户信息成功",
        "data": {
            "id": current_user.id,
            "name": current_user.name,
            "username": current_user.name,
            "role": getattr(current_user, 'role', 'user')  # 🆕 添加角色信息
        }
    }

@router.post("/token")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    """
    OAuth2 兼容的登录接口
    """
    user = db.query(models.User).filter(models.User.name == form_data.username).first()
    
    if not user or not security.verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    access_token = security.create_access_token(data={"sub": user.name})
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.name
    }