from pydantic_settings import BaseSettings
from typing import List, ClassVar
from pydantic import AnyHttpUrl
from dotenv import load_dotenv

load_dotenv()  # This loads the .env file at the root of your project

class Settings(BaseSettings):
    API_V1: ClassVar[str] = "/api/v1"
    PROJECT_NAME: str = "Final Year Project"
    
    BACKEND_CORS_ORIGINS: List[str] = ['*']

    # Database settings
    DATABASE_URL: str = "sqlite:///./sql_app.db"
    
    # JWT settings
    SECRET_KEY: str = "YOUR_SECRET_KEY_HERE"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

settings = Settings()