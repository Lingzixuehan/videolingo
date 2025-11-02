from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import timedelta

from database import get_db, engine
from models import Base, User
from schemas import UserCreate, UserResponse, Token
from auth import (
    get_password_hash, 
    verify_password, 
    create_access_token, 
    verify_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Videolingo Auth API")

# HTTP Bearer认证
security = HTTPBearer()

# 依赖项：获取当前用户
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    email = verify_token(credentials.credentials)
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在"
        )
    return user

# 注册接口
@app.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # 检查邮箱是否已存在
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册"
        )
    
    # 验证密码长度
    if len(user_data.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码至少6位"
        )
    
    # 创建新用户
    hashed_password = get_password_hash(user_data.password)
    db_user = User(email=user_data.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

# 登录接口
@app.post("/login", response_model=Token)
def login(user_data: UserCreate, db: Session = Depends(get_db)):
    # 查找用户
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误"
        )
    
    # 验证密码
    if not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误"
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# 受保护的用户信息接口
@app.get("/users/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

# 健康检查
@app.get("/")
def root():
    return {"message": "Videolingo Auth API 运行中"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)