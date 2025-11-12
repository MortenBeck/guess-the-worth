import os
from typing import List, Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL")

    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY")
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60 * 24 * 7

    secret_key: Optional[str] = os.getenv("SECRET_KEY")
    algorithm: Optional[str] = os.getenv("ALGORITHM")
    access_token_expire_minutes: Optional[str] = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

    auth0_domain: str = os.getenv("AUTH0_DOMAIN")
    auth0_client_id: str = os.getenv("AUTH0_CLIENT_ID")
    auth0_client_secret: str = os.getenv("AUTH0_CLIENT_SECRET")
    auth0_audience: str = os.getenv("AUTH0_AUDIENCE")

    stripe_secret_key: str = os.getenv("STRIPE_SECRET_KEY")
    stripe_publishable_key: str = os.getenv("STRIPE_PUBLISHABLE_KEY")
    stripe_webhook_secret: Optional[str] = os.getenv("STRIPE_WEBHOOK_SECRET")

    upload_dir: str = os.getenv("UPLOAD_DIR")
    max_file_size: int = os.getenv("MAX_FILE_SIZE")

    allowed_origins: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    cors_origins: Optional[str] = os.getenv("CORS_ORIGINS")

    environment: Optional[str] = os.getenv("ENVIRONMENT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if self.cors_origins:
            self.allowed_origins = [origin.strip() for origin in self.cors_origins.split(",")]


settings = Settings()
