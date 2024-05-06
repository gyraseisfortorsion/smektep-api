from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    REFRESH_SECRET_KEY: str
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    ALGORITHM: str
    OPENAI_API_KEY: str
    PASSWORD: str
    AWS_ACCESS_KEY1: str
    AWS_SECRET_KEY1: str
    GOOGLE_API_KEY: str
    class Config:
        env_file = ".env"

settings = Settings()