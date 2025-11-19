from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENV: str = "dev"
    PORT: int = 8000
    VERSION: str = "0.1.0"

    # 新增：鉴权与数据库
    SECRET_KEY: str = "xLLe3xMlr_8YM9EItIYMlJobZ19cA2uzT0R50DK08096tWozVua4JaJkNrLcRyz_whncnKHk7C8x-5mtjfy9gA"  # 生产改为环境变量
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    DATABASE_URL: str = "sqlite:///./videolingo.db"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
