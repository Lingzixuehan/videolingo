from pydantic import BaseModel, EmailStr
from typing import Optional

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