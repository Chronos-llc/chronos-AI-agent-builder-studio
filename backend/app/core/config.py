from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Chronos AI Agent Builder Studio"
    API_HOST: str = Field(default="0.0.0.0", env="API_HOST")
    API_PORT: int = Field(default=8000, env="API_PORT")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # Database - Use SQLite for development by default
    DATABASE_URL: str = Field(default="sqlite+aiosqlite:///./chronos.db", env="DATABASE_URL")
    
    # Redis
    REDIS_URL: str = Field(default="redis-11166.c277.us-east-1-3.ec2.cloud.redislabs.com:11166", env="REDIS_URL")
    
    # JWT Configuration
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # CORS
    ALLOWED_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
        ],
        env="ALLOWED_ORIGINS"
    )
    
    # Security
    PASSWORD_MIN_LENGTH: int = Field(default=8, env="PASSWORD_MIN_LENGTH")
    MAX_LOGIN_ATTEMPTS: int = Field(default=5, env="MAX_LOGIN_ATTEMPTS")
    LOCKOUT_DURATION_MINUTES: int = Field(default=15, env="LOCKOUT_DURATION_MINUTES")
    
    # Email Configuration
    SMTP_HOST: Optional[str] = Field(default=None, env="SMTP_HOST")
    SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
    SMTP_USER: Optional[str] = Field(default=None, env="SMTP_USER")
    SMTP_PASSWORD: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    
    # External API Keys
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    FIREWORKS_API_KEY: Optional[str] = Field(default=None, env="FIREWORKS_API_KEY")
    XAI_API_KEY: Optional[str] = Field(default=None, env="XAI_API_KEY")
    OPENROUTER_API_KEY: Optional[str] = Field(default=None, env="OPENROUTER_API_KEY")
    
    # Voice and Speech Provider Keys
    ELEVENLABS_API_KEY: Optional[str] = Field(default=None, env="ELEVENLABS_API_KEY")
    GOOGLE_CLOUD_API_KEY: Optional[str] = Field(default=None, env="GOOGLE_CLOUD_API_KEY")
    AZURE_SPEECH_KEY: Optional[str] = Field(default=None, env="AZURE_SPEECH_KEY")
    AWS_ACCESS_KEY_ID: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    AWS_REGION: Optional[str] = Field(default=None, env="AWS_REGION")
    DEEPGRAM_API_KEY: Optional[str] = Field(default=None, env="DEEPGRAM_API_KEY")
    ASSEMBLYAI_API_KEY: Optional[str] = Field(default=None, env="ASSEMBLYAI_API_KEY")
    VIRUSTOTAL_API_KEY: Optional[str] = Field(default=None, env="VIRUSTOTAL_API_KEY")
    VIRUSTOTAL_TIMEOUT_SECONDS: int = Field(default=10, env="VIRUSTOTAL_TIMEOUT_SECONDS")
    VIRUSTOTAL_POLL_ATTEMPTS: int = Field(default=5, env="VIRUSTOTAL_POLL_ATTEMPTS")
    SKILL_LOCAL_SUSPICIOUS_THRESHOLD: int = Field(default=40, env="SKILL_LOCAL_SUSPICIOUS_THRESHOLD")
    SKILL_LOCAL_MALICIOUS_THRESHOLD: int = Field(default=80, env="SKILL_LOCAL_MALICIOUS_THRESHOLD")
    
    # MCP Server Configuration
    MCP_SERVER_URL: Optional[str] = Field(default=None, env="MCP_SERVER_URL")
    MCP_SERVER_API_KEY: Optional[str] = Field(default=None, env="MCP_SERVER_API_KEY")
    MCP_SERVER_TIMEOUT: int = Field(default=30, env="MCP_SERVER_TIMEOUT")

    # E2B Virtual Computer
    E2B_API_KEY: Optional[str] = Field(default=None, env="E2B_API_KEY")

    # OAuth
    FRONTEND_BASE_URL: str = Field(default="http://localhost:5173", env="FRONTEND_BASE_URL")
    GOOGLE_OAUTH_CLIENT_ID: Optional[str] = Field(default=None, env="GOOGLE_OAUTH_CLIENT_ID")
    GOOGLE_OAUTH_CLIENT_SECRET: Optional[str] = Field(default=None, env="GOOGLE_OAUTH_CLIENT_SECRET")
    GOOGLE_OAUTH_REDIRECT_URI: Optional[str] = Field(default=None, env="GOOGLE_OAUTH_REDIRECT_URI")
    GITHUB_OAUTH_CLIENT_ID: Optional[str] = Field(default=None, env="GITHUB_OAUTH_CLIENT_ID")
    GITHUB_OAUTH_CLIENT_SECRET: Optional[str] = Field(default=None, env="GITHUB_OAUTH_CLIENT_SECRET")
    GITHUB_OAUTH_REDIRECT_URI: Optional[str] = Field(default=None, env="GITHUB_OAUTH_REDIRECT_URI")
    
    # Telephony provider credentials
    TWILIO_ACCOUNT_SID: Optional[str] = Field(default=None, env="TWILIO_ACCOUNT_SID")
    TWILIO_API_KEY: Optional[str] = Field(default=None, env="TWILIO_API_KEY")
    TWILIO_API_SECRET: Optional[str] = Field(default=None, env="TWILIO_API_SECRET")
    VONAGE_API_KEY: Optional[str] = Field(default=None, env="VONAGE_API_KEY")
    VONAGE_API_SECRET: Optional[str] = Field(default=None, env="VONAGE_API_SECRET")

    # File Storage Configuration
    UPLOAD_MAX_SIZE: int = Field(default=10 * 1024 * 1024, env="UPLOAD_MAX_SIZE")
    ALLOWED_FILE_TYPES: List[str] = Field(
        default=["txt", "pdf", "doc", "docx", "png", "jpg", "jpeg", "gif", "mp4", "avi", "mov"],
        env="ALLOWED_FILE_TYPES"
    )
    OBJECT_STORAGE_PROVIDER: str = Field(default="s3", env="OBJECT_STORAGE_PROVIDER")
    OBJECT_STORAGE_ENDPOINT_URL: Optional[str] = Field(
        default=None,
        env="OBJECT_STORAGE_ENDPOINT_URL",
    )
    OBJECT_STORAGE_REGION: str = Field(default="us-east-1", env="OBJECT_STORAGE_REGION")
    OBJECT_STORAGE_BUCKET: str = Field(default="chronos-objects", env="OBJECT_STORAGE_BUCKET")
    OBJECT_STORAGE_ACCESS_KEY_ID: Optional[str] = Field(
        default=None,
        env="OBJECT_STORAGE_ACCESS_KEY_ID",
    )
    OBJECT_STORAGE_SECRET_ACCESS_KEY: Optional[str] = Field(
        default=None,
        env="OBJECT_STORAGE_SECRET_ACCESS_KEY",
    )
    OBJECT_STORAGE_USE_SSL: bool = Field(default=True, env="OBJECT_STORAGE_USE_SSL")
    OBJECT_STORAGE_FORCE_PATH_STYLE: bool = Field(default=False, env="OBJECT_STORAGE_FORCE_PATH_STYLE")
    OBJECT_STORAGE_SIGNED_URL_TTL_SECONDS: int = Field(
        default=3600,
        env="OBJECT_STORAGE_SIGNED_URL_TTL_SECONDS",
    )
    OBJECT_STORAGE_BASE_PREFIX: str = Field(default="chronos", env="OBJECT_STORAGE_BASE_PREFIX")
    OBJECT_STORAGE_AUTO_CREATE_BUCKET: bool = Field(
        default=False,
        env="OBJECT_STORAGE_AUTO_CREATE_BUCKET",
    )

    # WebSocket Configuration
    WEBSOCKET_HEARTBEAT_INTERVAL: int = Field(default=30, env="WEBSOCKET_HEARTBEAT_INTERVAL")
    WEBSOCKET_PING_TIMEOUT: int = Field(default=10, env="WEBSOCKET_PING_TIMEOUT")

    # Development Server Configuration
    RELOAD: bool = Field(default=False, env="RELOAD")
    WORKERS: int = Field(default=1, env="WORKERS")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Create settings instance
settings = Settings()
