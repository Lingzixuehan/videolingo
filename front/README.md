## 环境变量（前端）
复制 `.env.example` 为 `.env.local` 并设置后端地址：
VITE_API_BASE=http://127.0.0.1:8000

运行时 `import.meta.env.VITE_API_BASE` 将用于统一 API 客户端。

