## 环境变量（前端）
复制 `.env.example` 为 `.env.local` 并设置后端地址：
VITE_API_BASE=http://127.0.0.1:8000

运行时 `import.meta.env.VITE_API_BASE` 将用于统一 API 客户端。

## 开发直通登录
开发环境或设置 `VITE_DEV_LOGIN=1` 时，可使用：
用户名/邮箱: test
密码: test
跳过后端直接获得 DEV_TOKEN（仅开发用）。