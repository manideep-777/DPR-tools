from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "MSME DPR Generator"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:3001"
    
    # File Upload
    UPLOAD_DIR: str = "storage/uploads"
    ALLOWED_EXTENSIONS: str = "pdf,doc,docx,jpg,jpeg,png"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # AI Service
    GEMINI_API_KEY: str = "your-gemini-api-key-here"
    
    # PDF Generation
    PDF_OUTPUT_DIR: str = "storage/generated_dprs"
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        return [ext.strip() for ext in self.ALLOWED_EXTENSIONS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
