from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any, Dict
from datetime import datetime

# 用户注册请求模型
class UserCreate(BaseModel):
    email: EmailStr
    password: str

# 用户响应模型
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    
    class Config:
        orm_mode = True

# Token响应模型
class Token(BaseModel):
    access_token: str
    token_type: str

# Token数据模型
class TokenData(BaseModel):
    email: Optional[str] = None

# 卡片创建请求模型
class CardCreate(BaseModel):
    video_id: str
    timestamp: Optional[float] = None
    tags: Optional[str] = None
    content: Dict[str, Any]  # JSON内容

# 卡片更新请求模型  
class CardUpdate(BaseModel):
    timestamp: Optional[float] = None
    tags: Optional[str] = None
    content: Optional[Dict[str, Any]] = None

# 卡片响应模型
class CardResponse(BaseModel):
    id: int
    video_id: str
    timestamp: Optional[float]
    tags: Optional[str]
    content: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# 卡片列表响应模型
class CardListResponse(BaseModel):
    cards: List[CardResponse]
    total: int