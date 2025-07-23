"""
Configuration settings for HealthGenie Healthcare Assistant
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings using Pydantic BaseSettings"""
    
    # API Keys
    GOOGLE_AI_API_KEY: str = Field(default="", description="Google AI API key for Gemini models")
    SERP_API_KEY: str = Field(..., description="SERP API key for hospital search")
    
    # Model Configuration
    MODEL_NAME: str = "gemini-2.5-flash"
    TEMPERATURE: float = 0.1
    MAX_TOKENS: int = 4000
    
    # Application Configuration
    APP_NAME: str = "HealthGenie"
    DEBUG: bool = False
    MAX_FILE_SIZE_MB: int = 10
    
    # File Format Configuration
    SUPPORTED_IMAGE_FORMATS: List[str] = ['.jpg', '.jpeg', '.png', '.bmp']
    SUPPORTED_DOCUMENT_FORMATS: List[str] = ['.pdf', '.txt', '.docx', '.jpg', '.jpeg', '.png']
    
    # Hospital Search Configuration
    SEARCH_LOCATION: str = "India"
    MAX_HOSPITALS: int = 5
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

def get_google_ai_api_key():
    """Get Google AI API key from environment variables (supports both old and new names)"""
    # Try GOOGLE_AI_API_KEY first
    api_key = os.getenv('GOOGLE_AI_API_KEY')
    if api_key:
        return api_key
    
    # Try legacy GEMINI_API_KEY
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        return api_key
    
    raise ValueError(
        "Google AI API key is required. Please set either GOOGLE_AI_API_KEY or GEMINI_API_KEY in your .env file"
    )

# Initialize settings
try:
    config = Settings()
    # Override the API key if it's empty
    if not config.GOOGLE_AI_API_KEY:
        config.GOOGLE_AI_API_KEY = get_google_ai_api_key()
except Exception as e:
    print(f"Configuration error: {e}")
    print("Please check your .env file and ensure it contains the required API keys.")
    print("\nRequired .env file format:")
    print("GEMINI_API_KEY=your_gemini_api_key_here")
    print("SERP_API_KEY=your_serp_api_key_here")
    raise 