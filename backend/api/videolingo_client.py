"""
Videolingo 卡片同步 API - Python 客户端库

这个库提供了一个简便的 Python 接口来与 Videolingo 卡片同步 API 交互。

使用示例：
    from videolingo_client import VideolingoClient
    
    client = VideolingoClient(base_url="http://localhost:8000")
    
    # 注册和登录
    client.register("user@example.com", "password123")
    token = client.login("user@example.com", "password123")
    
    # 创建卡片
    card = client.create_card(
        video_id="video_001",
        timestamp=123.45,
        tags="Python,API",
        content={"title": "学习笔记"}
    )
    
    # 查询卡片
    cards = client.list_cards(video_id="video_001")
    
    # 更新卡片
    updated_card = client.update_card(card["id"], tags="Python,API,Updated")
    
    # 删除卡片
    client.delete_card(card["id"])
"""

import requests
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CardResponse:
    """卡片响应数据"""
    id: int
    video_id: str
    timestamp: Optional[float]
    tags: Optional[str]
    content: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """从字典创建 CardResponse 对象"""
        return cls(
            id=data["id"],
            video_id=data["video_id"],
            timestamp=data.get("timestamp"),
            tags=data.get("tags"),
            content=data["content"],
            created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00"))
        )


class VideolingoClientError(Exception):
    """Videolingo 客户端异常"""
    pass


class VideolingoClient:
    """Videolingo 卡片同步 API 客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 10):
        """
        初始化客户端
        
        Args:
            base_url: API 基础 URL
            timeout: 请求超时时间（秒）
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.access_token: Optional[str] = None
        self.session = requests.Session()
    
    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        headers = {"Content-Type": "application/json"}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        发送 HTTP 请求
        
        Args:
            method: HTTP 方法
            endpoint: API 端点
            **kwargs: 请求参数
            
        Returns:
            响应 JSON
            
        Raises:
            VideolingoClientError: 当请求失败时
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()
        
        try:
            response = self.session.request(
                method,
                url,
                headers=headers,
                timeout=self.timeout,
                **kwargs
            )
            
            # 处理 204 No Content
            if response.status_code == 204:
                return {}
            
            # 处理错误响应
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                    error_msg = error_data.get("detail", "Unknown error")
                except:
                    error_msg = response.text
                raise VideolingoClientError(
                    f"HTTP {response.status_code}: {error_msg}"
                )
            
            return response.json()
        
        except requests.RequestException as e:
            raise VideolingoClientError(f"Request failed: {str(e)}")
    
    # ==================== 认证相关 ====================
    
    def register(self, email: str, password: str) -> Dict[str, Any]:
        """
        注册新用户
        
        Args:
            email: 用户邮箱
            password: 用户密码
            
        Returns:
            用户信息
        """
        data = {"email": email, "password": password}
        return self._make_request("POST", "/register", json=data)
    
    def login(self, email: str, password: str) -> str:
        """
        用户登录
        
        Args:
            email: 用户邮箱
            password: 用户密码
            
        Returns:
            访问令牌
        """
        data = {"email": email, "password": password}
        response = self._make_request("POST", "/login", json=data)
        self.access_token = response["access_token"]
        return self.access_token
    
    def set_token(self, token: str) -> None:
        """
        设置访问令牌
        
        Args:
            token: JWT 访问令牌
        """
        self.access_token = token
    
    def get_current_user(self) -> Dict[str, Any]:
        """
        获取当前用户信息
        
        Returns:
            用户信息
        """
        if not self.access_token:
            raise VideolingoClientError("Not logged in")
        return self._make_request("GET", "/users/me")
    
    # ==================== 卡片操作 ====================
    
    def create_card(
        self,
        video_id: str,
        content: Dict[str, Any],
        timestamp: Optional[float] = None,
        tags: Optional[str] = None
    ) -> CardResponse:
        """
        创建新卡片
        
        Args:
            video_id: 视频 ID
            content: 卡片内容（JSON 格式）
            timestamp: 视频时间戳（可选）
            tags: 标签，多个标签用逗号分隔（可选）
            
        Returns:
            创建的卡片信息
        """
        if not self.access_token:
            raise VideolingoClientError("Not logged in")
        
        data = {
            "video_id": video_id,
            "content": content,
        }
        if timestamp is not None:
            data["timestamp"] = timestamp
        if tags is not None:
            data["tags"] = tags
        
        response = self._make_request("POST", "/cards", json=data)
        return CardResponse.from_dict(response)
    
    def list_cards(
        self,
        video_id: Optional[str] = None,
        timestamp_from: Optional[float] = None,
        timestamp_to: Optional[float] = None,
        tags: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        查询卡片列表
        
        Args:
            video_id: 按视频 ID 筛选（可选）
            timestamp_from: 时间戳范围下限（可选）
            timestamp_to: 时间戳范围上限（可选）
            tags: 按标签筛选（可选）
            skip: 跳过的记录数（分页）
            limit: 返回的最大记录数
            
        Returns:
            包含卡片列表和总数的字典
        """
        if not self.access_token:
            raise VideolingoClientError("Not logged in")
        
        params = {"skip": skip, "limit": limit}
        if video_id is not None:
            params["video_id"] = video_id
        if timestamp_from is not None:
            params["timestamp_from"] = timestamp_from
        if timestamp_to is not None:
            params["timestamp_to"] = timestamp_to
        if tags is not None:
            params["tags"] = tags
        
        response = self._make_request("GET", "/cards", params=params)
        
        # 转换卡片列表
        cards = [CardResponse.from_dict(card) for card in response["cards"]]
        return {
            "cards": cards,
            "total": response["total"]
        }
    
    def get_card(self, card_id: int) -> CardResponse:
        """
        获取单个卡片
        
        Args:
            card_id: 卡片 ID
            
        Returns:
            卡片信息
        """
        if not self.access_token:
            raise VideolingoClientError("Not logged in")
        
        response = self._make_request("GET", f"/cards/{card_id}")
        return CardResponse.from_dict(response)
    
    def update_card(
        self,
        card_id: int,
        timestamp: Optional[float] = None,
        tags: Optional[str] = None,
        content: Optional[Dict[str, Any]] = None
    ) -> CardResponse:
        """
        更新卡片
        
        Args:
            card_id: 卡片 ID
            timestamp: 新的时间戳（可选）
            tags: 新的标签（可选）
            content: 新的内容（可选）
            
        Returns:
            更新后的卡片信息
        """
        if not self.access_token:
            raise VideolingoClientError("Not logged in")
        
        data = {}
        if timestamp is not None:
            data["timestamp"] = timestamp
        if tags is not None:
            data["tags"] = tags
        if content is not None:
            data["content"] = content
        
        response = self._make_request("PUT", f"/cards/{card_id}", json=data)
        return CardResponse.from_dict(response)
    
    def delete_card(self, card_id: int) -> bool:
        """
        删除卡片
        
        Args:
            card_id: 卡片 ID
            
        Returns:
            True if successful
        """
        if not self.access_token:
            raise VideolingoClientError("Not logged in")
        
        self._make_request("DELETE", f"/cards/{card_id}")
        return True
    
    def search_cards(
        self,
        video_id: Optional[str] = None,
        tags: Optional[str] = None,
        **kwargs
    ) -> List[CardResponse]:
        """
        搜索卡片（便捷方法）
        
        Args:
            video_id: 视频 ID
            tags: 标签
            **kwargs: 其他筛选参数
            
        Returns:
            卡片列表
        """
        result = self.list_cards(video_id=video_id, tags=tags, **kwargs)
        return result["cards"]
    
    def close(self) -> None:
        """关闭 HTTP 会话"""
        self.session.close()
    
    def __enter__(self):
        """支持 with 语句"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """支持 with 语句"""
        self.close()


# ==================== 便捷函数 ====================

def create_client(
    email: str,
    password: str,
    base_url: str = "http://localhost:8000"
) -> VideolingoClient:
    """
    创建并登录客户端（便捷函数）
    
    Args:
        email: 用户邮箱
        password: 用户密码
        base_url: API 基础 URL
        
    Returns:
        已登录的客户端
    """
    client = VideolingoClient(base_url=base_url)
    try:
        client.login(email, password)
    except VideolingoClientError:
        # 如果登录失败，尝试注册
        client.register(email, password)
        client.login(email, password)
    return client


# ==================== 示例使用 ====================

if __name__ == "__main__":
    # 示例：使用客户端库
    
    print("=" * 60)
    print("Videolingo 卡片同步 API - Python 客户端库示例")
    print("=" * 60)
    
    try:
        # 创建并登录客户端
        client = create_client(
            email="test@example.com",
            password="password123",
            base_url="http://localhost:8000"
        )
        print("✓ 已登录")
        
        # 获取当前用户信息
        user = client.get_current_user()
        print(f"✓ 当前用户: {user['email']}")
        
        # 创建卡片
        print("\n--- 创建卡片 ---")
        card = client.create_card(
            video_id="video_001",
            timestamp=123.45,
            tags="Python,API",
            content={
                "title": "Python 学习笔记",
                "description": "关于 API 的笔记",
                "key_points": ["点1", "点2", "点3"]
            }
        )
        print(f"✓ 卡片已创建，ID: {card.id}")
        print(f"  标题: {card.content['title']}")
        
        # 查询卡片
        print("\n--- 查询卡片 ---")
        result = client.list_cards(video_id="video_001")
        print(f"✓ 找到 {result['total']} 张卡片")
        for card in result["cards"]:
            print(f"  - ID {card.id}: {card.content.get('title', 'No title')}")
        
        # 按标签搜索
        print("\n--- 按标签搜索 ---")
        cards = client.search_cards(tags="API")
        print(f"✓ 找到 {len(cards)} 张含有 'API' 标签的卡片")
        
        # 更新卡片
        if result["cards"]:
            print("\n--- 更新卡片 ---")
            first_card = result["cards"][0]
            updated = client.update_card(
                first_card.id,
                tags="Python,API,Updated",
                content={
                    "title": "更新的 Python 学习笔记",
                    "description": "已更新的描述"
                }
            )
            print(f"✓ 卡片已更新: {updated.content['title']}")
        
        # 删除卡片
        if len(result["cards"]) > 1:
            print("\n--- 删除卡片 ---")
            second_card = result["cards"][1]
            if client.delete_card(second_card.id):
                print(f"✓ 卡片已删除 (ID: {second_card.id})")
        
        print("\n" + "=" * 60)
        print("✓ 所有示例执行完毕")
        print("=" * 60)
    
    except VideolingoClientError as e:
        print(f"✗ 错误: {e}")
    
    finally:
        client.close()
