"""
Configuration file for HealthGenie App

This module uses Pydantic's BaseSettings (from pydantic_settings)
to load environment variables from a .env file for secure and modular configuration management.

Required environment variables (set in .env):
- GEMINI_API_KEY: Your Google Gemini API key
- SERP_API_KEY: Your SERP API key

Other settings can be customized here as needed.
"""
from pydantic_settings import BaseSettings  # Updated import for Pydantic v2+
from pydantic import Field
from typing import List

class AppConfig(BaseSettings):
    """
    Application configuration loaded from environment variables.
    Uses Pydantic BaseSettings for type safety and validation.
    """
    # API Keys (must be set in .env)
    GEMINI_API_KEY: str = Field(..., env="GEMINI_API_KEY")
    SERP_API_KEY: str = Field(..., env="SERP_API_KEY")

    # Gemini Model Configuration
    GEMINI_IMAGE_MODEL: str = "gemini-2.5-flash"         # For X-ray and report image analysis
    GEMINI_TEXT_MODEL: str = "gemini-2.5-flash"          # For summarization/meal plan (or use "gemini-2.5-flash-lite")

    # Application Settings
    MAX_FILE_SIZE_MB: int = 10
    SUPPORTED_IMAGE_FORMATS: List[str] = [".jpg", ".jpeg", ".png", ".bmp"]
    SUPPORTED_DOCUMENT_FORMATS: List[str] = [".pdf", ".jpg", ".jpeg", ".png"]

    # Hospital Search Configuration
    SEARCH_LOCATION: str = "India"
    MAX_HOSPITALS: int = 5

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Singleton config instance for use throughout the app
config = AppConfig() 