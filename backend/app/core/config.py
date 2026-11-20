import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    PROJECT_NAME: str = "AI Agent Agency Master"
    VERSION: str = "2.0.0"
    
    # PostgreSQL Configuration
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_NAME: str = os.getenv("DB_NAME", "agency_master")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "Rajesh@123")
    
    # AI Model Key
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Outreach Configuration
    MESSAGING_PROVIDER: str = os.getenv("MESSAGING_PROVIDER", "console_mock")

settings = Settings()
