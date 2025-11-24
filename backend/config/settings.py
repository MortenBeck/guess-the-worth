from typing import List, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database Configuration - REQUIRED
    database_url: str

    # JWT Configuration - REQUIRED for security
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60 * 24 * 7  # 7 days

    # Legacy fields (kept for backward compatibility)
    secret_key: Optional[str] = None
    algorithm: Optional[str] = None
    access_token_expire_minutes: Optional[str] = None

    # Auth0 Configuration - REQUIRED for authentication
    auth0_domain: str
    auth0_client_id: str
    auth0_client_secret: str
    auth0_audience: str

    # Stripe Configuration - OPTIONAL (empty strings are acceptable)
    stripe_secret_key: str = ""
    stripe_publishable_key: str = ""
    stripe_webhook_secret: Optional[str] = None

    # File Upload Configuration
    upload_dir: str = "./uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB

    # CORS Configuration
    allowed_origins: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    cors_origins: Optional[str] = None

    # Environment
    environment: str = "development"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Override allowed_origins if cors_origins is provided
        if self.cors_origins:
            self.allowed_origins = [origin.strip() for origin in self.cors_origins.split(",")]

        # Validate required secrets are not using default/placeholder values (skip in test mode)
        import sys
        if "pytest" not in sys.modules:
            self._validate_secrets()

    def _validate_secrets(self):
        """Validate that required secrets are properly configured."""
        # Check for placeholder values in critical secrets
        if "your-" in self.jwt_secret_key.lower() or len(self.jwt_secret_key) < 32:
            raise ValueError(
                "JWT_SECRET_KEY must be set to a secure value (at least 32 characters). "
                "Generate one using: openssl rand -hex 32"
            )

        if "your-" in self.auth0_client_secret.lower() or len(self.auth0_client_secret) < 20:
            raise ValueError(
                "AUTH0_CLIENT_SECRET must be set to your actual Auth0 client secret. "
                "Get it from: https://manage.auth0.com/"
            )

        if "your-" in self.auth0_domain.lower():
            raise ValueError(
                "AUTH0_DOMAIN must be set to your actual Auth0 domain. "
                "Example: your-tenant.auth0.com"
            )

        if "your-" in self.auth0_client_id.lower():
            raise ValueError(
                "AUTH0_CLIENT_ID must be set to your actual Auth0 client ID. "
                "Get it from: https://manage.auth0.com/"
            )


settings = Settings()
