from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import timedelta

from database import get_db, engine
from models import Base, User, Card, AuditLog
from schemas import (
    UserCreate, UserResponse, Token, CardCreate, CardUpdate,
    CardResponse, CardListResponse, UserDeleteRequest,
    AuditLogResponse, AuditLogListResponse
)
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

# 依赖项：获取当前管理员用户
def get_current_admin(
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return current_user

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

# ==================== 卡片同步 API ====================

# 上传卡片
@app.post("/cards", response_model=CardResponse)
def create_card(
    card_data: CardCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    上传新卡片
    - **video_id**: 视频ID（必需）
    - **timestamp**: 卡片时间戳（可选）
    - **tags**: 标签，多个标签用逗号分隔（可选）
    - **content**: JSON 内容（必需）
    """
    db_card = Card(
        user_id=current_user.id,
        video_id=card_data.video_id,
        timestamp=card_data.timestamp,
        tags=card_data.tags,
        content=card_data.content
    )
    db.add(db_card)
    db.commit()
    db.refresh(db_card)
    return db_card

# 查询卡片列表
@app.get("/cards", response_model=CardListResponse)
def list_cards(
    video_id: str = None,
    timestamp_from: float = None,
    timestamp_to: float = None,
    tags: str = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    查询卡片列表，支持多种筛选条件
    - **video_id**: 按视频ID筛选
    - **timestamp_from**: 时间戳范围（开始）
    - **timestamp_to**: 时间戳范围（结束）
    - **tags**: 按标签筛选（模糊匹配）
    - **skip**: 跳过的记录数（分页）
    - **limit**: 返回的记录数（分页）
    """
    query = db.query(Card).filter(Card.user_id == current_user.id)
    
    # 按视频ID筛选
    if video_id:
        query = query.filter(Card.video_id == video_id)
    
    # 按时间戳范围筛选
    if timestamp_from is not None:
        query = query.filter(Card.timestamp >= timestamp_from)
    if timestamp_to is not None:
        query = query.filter(Card.timestamp <= timestamp_to)
    
    # 按标签筛选
    if tags:
        query = query.filter(Card.tags.ilike(f"%{tags}%"))
    
    # 获取总数
    total = query.count()
    
    # 排序并分页
    cards = query.order_by(Card.created_at.desc()).offset(skip).limit(limit).all()
    
    return {"cards": cards, "total": total}

# 获取单个卡片
@app.get("/cards/{card_id}", response_model=CardResponse)
def get_card(
    card_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取指定ID的卡片
    """
    card = db.query(Card).filter(
        Card.id == card_id,
        Card.user_id == current_user.id
    ).first()
    
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="卡片不存在"
        )
    
    return card

# 更新卡片
@app.put("/cards/{card_id}", response_model=CardResponse)
def update_card(
    card_id: int,
    card_data: CardUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新卡片信息
    - **timestamp**: 更新时间戳（可选）
    - **tags**: 更新标签（可选）
    - **content**: 更新JSON内容（可选）
    """
    card = db.query(Card).filter(
        Card.id == card_id,
        Card.user_id == current_user.id
    ).first()
    
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="卡片不存在"
        )
    
    # 更新字段
    if card_data.timestamp is not None:
        card.timestamp = card_data.timestamp
    if card_data.tags is not None:
        card.tags = card_data.tags
    if card_data.content is not None:
        card.content = card_data.content
    
    db.commit()
    db.refresh(card)
    return card

# 删除卡片
@app.delete("/cards/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_card(
    card_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除指定ID的卡片
    """
    card = db.query(Card).filter(
        Card.id == card_id,
        Card.user_id == current_user.id
    ).first()
    
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="卡片不存在"
        )
    
    db.delete(card)
    db.commit()

# 健康检查
@app.get("/")
def root():
    return {"message": "Videolingo Auth API 运行中"}

# ==================== 管理员 API ====================

# 管理员删除用户
@app.delete("/admin/users/{user_id}", status_code=status.HTTP_200_OK)
def admin_delete_user(
    user_id: int,
    delete_request: UserDeleteRequest,
    admin_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    管理员删除用户接口
    - **user_id**: 要删除的用户ID
    - **reason**: 删除理由（必填）

    返回：操作成功消息（不包含敏感信息）
    """
    # 查找要删除的用户
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 防止管理员删除自己
    if target_user.id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己"
        )

    # 记录审计日志
    audit_log = AuditLog(
        action="delete_user",
        operator_id=admin_user.id,
        target_user_id=target_user.id,
        reason=delete_request.reason,
        details={
            "operator_email": admin_user.email,
            "deleted_user_id": target_user.id
        }
    )
    db.add(audit_log)

    # 删除用户相关的卡片
    db.query(Card).filter(Card.user_id == user_id).delete()

    # 删除用户
    db.delete(target_user)
    db.commit()

    return {
        "message": "用户删除成功",
        "deleted_user_id": user_id,
        "audit_log_id": audit_log.id
    }

# 查询审计日志
@app.get("/admin/audit-logs", response_model=AuditLogListResponse)
def get_audit_logs(
    action: str = None,
    operator_id: int = None,
    target_user_id: int = None,
    skip: int = 0,
    limit: int = 100,
    admin_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    查询审计日志
    - **action**: 按操作类型筛选（如 'delete_user'）
    - **operator_id**: 按操作人ID筛选
    - **target_user_id**: 按被操作用户ID筛选
    - **skip**: 跳过的记录数（分页）
    - **limit**: 返回的记录数（分页）
    """
    query = db.query(AuditLog)

    # 按操作类型筛选
    if action:
        query = query.filter(AuditLog.action == action)

    # 按操作人筛选
    if operator_id:
        query = query.filter(AuditLog.operator_id == operator_id)

    # 按被操作用户筛选
    if target_user_id:
        query = query.filter(AuditLog.target_user_id == target_user_id)

    # 获取总数
    total = query.count()

    # 排序并分页
    logs = query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()

    return {"logs": logs, "total": total}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)