import os
from pydantic_settings import BaseSettings
from typing import Optional, List

class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:password@localhost:5432/guess_the_worth_db"

    jwt_secret_key: str = "your-super-secret-jwt-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60 * 24 * 7

    secret_key: Optional[str] = None
    algorithm: Optional[str] = None
    access_token_expire_minutes: Optional[str] = None

    auth0_domain: str = "guess-the-worth.eu.auth0.com"
    auth0_client_id: str = "M5WxOcqdtVR3PuEQrirdkMyQnpRMTtCI"
    auth0_client_secret: str = "shtVFlC5lheEetG6Vlc5vSmdT_w4-mvFvrbFoDG1CCj4BYgSf49eH3Lit2OPFe4B"
    auth0_audience: str = "https://api.guesstheworth.com"

    stripe_secret_key: str = ""
    stripe_publishable_key: str = ""
    stripe_webhook_secret: Optional[str] = None

    upload_dir: str = "./uploads"
    max_file_size: int = 10 * 1024 * 1024

    allowed_origins: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    cors_origins: Optional[str] = None

    environment: Optional[str] = "development"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if self.cors_origins:
            self.allowed_origins = [origin.strip() for origin in self.cors_origins.split(',')]

settings = Settings()