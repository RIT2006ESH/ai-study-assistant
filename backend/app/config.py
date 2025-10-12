"""
Application configuration settings
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Application
    app_name: str = "AI Study Assistant"
    debug: bool = True
    environment: str = "development"
    
    # Database
    database_url: str = "sqlite+aiosqlite:///./ai_study.db"
    
    # Security & Authentication
    secret_key: str = "your-secret-key-here-change-in-production-minimum-32-characters-long"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours (was 30 minutes)
    
    # AI/LLM API Keys
    gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    
    # Default LLM Provider
    default_llm_provider: str = "gemini"  # Options: gemini, openai, anthropic, groq
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    redis_enabled: bool = False  # Set to True if using Redis for caching
    
    # CORS Settings
    cors_origins: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
    ]
    
    # File Upload Settings
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: list = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
        "application/msword",  # .doc
        "text/plain",
        "image/jpeg",
        "image/png",
        "image/gif",
    ]
    upload_dir: str = "./uploads"
    
    # Document Processing
    max_text_length: int = 100000  # Maximum characters for text processing
    chunk_size: int = 3000  # Default chunk size for long documents
    chunk_overlap: int = 200  # Overlap between chunks
    
    # LLM Generation Settings
    default_temperature: float = 0.7
    default_max_tokens: int = 2000
    
    # Rate Limiting
    rate_limit_enabled: bool = False
    requests_per_minute: int = 60
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "./logs/app.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"  # Allow extra fields from .env

settings = Settings()

# Validate settings on startup
def validate_settings():
    """Validate critical settings"""
    errors = []
    
    # Check if at least one LLM API key is configured
    if not any([
        settings.gemini_api_key,
        settings.openai_api_key,
        settings.anthropic_api_key,
        settings.groq_api_key
    ]):
        errors.append("⚠️  No LLM API key configured. Please set at least one API key in .env file.")
    
    # Warn about default secret key
    if settings.secret_key == "your-secret-key-here-change-in-production-minimum-32-characters-long":
        errors.append("⚠️  Using default SECRET_KEY. Please change it in production!")
    
    # Create upload directory if it doesn't exist
    if not os.path.exists(settings.upload_dir):
        os.makedirs(settings.upload_dir)
        print(f"✅ Created upload directory: {settings.upload_dir}")
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(settings.log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
        print(f"✅ Created logs directory: {log_dir}")
    
    # Print warnings
    if errors:
        print("\n" + "="*60)
        print("CONFIGURATION WARNINGS:")
        for error in errors:
            print(error)
        print("="*60 + "\n")
    
    # Print active configuration
    print("\n" + "="*60)
    print("ACTIVE CONFIGURATION:")
    print(f"App Name: {settings.app_name}")
    print(f"Environment: {settings.environment}")
    print(f"Debug Mode: {settings.debug}")
    print(f"Database: {settings.database_url}")
    print(f"Default LLM: {settings.default_llm_provider}")
    print(f"Gemini API: {'✅ Configured' if settings.gemini_api_key else '❌ Not configured'}")
    print(f"OpenAI API: {'✅ Configured' if settings.openai_api_key else '❌ Not configured'}")
    print(f"Anthropic API: {'✅ Configured' if settings.anthropic_api_key else '❌ Not configured'}")
    print(f"Groq API: {'✅ Configured' if settings.groq_api_key else '❌ Not configured'}")
    print(f"Redis: {'✅ Enabled' if settings.redis_enabled else '❌ Disabled'}")
    print(f"Upload Directory: {settings.upload_dir}")
    print(f"Max File Size: {settings.max_file_size / (1024*1024):.1f}MB")
    print("="*60 + "\n")

# Call validation on import (optional - comment out if you don't want this)
validate_settings()