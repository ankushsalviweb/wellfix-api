import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from functools import lru_cache

# Load .env file if it exists
load_dotenv()

# Helper function to clean environment variable values
def get_env_var(name, default=None):
    """
    Get environment variable value with proper cleaning of comments and whitespace.
    
    This function handles both inline comments (e.g., "1440 # 1 day") and 
    trailing whitespace in environment variable values.
    """
    value = os.environ.get(name, default)
    if value and isinstance(value, str):
        # Strip any inline comments from the value
        if '#' in value:
            value = value.split('#')[0].strip()
        # Strip any trailing/leading whitespace
        value = value.strip()
    return value

class Settings(BaseSettings):
    # --- Project Info ---
    PROJECT_NAME: str = "WellFix API"
    API_V1_STR: str = "/api/v1"

    # --- Database Settings ---
    # For testing/development, provide a fallback
    DATABASE_URL: str = get_env_var("DATABASE_URL", "postgresql://user:password@localhost:5432/wellfixdb")

    # --- JWT Settings ---
    # Generate a secure secret key: openssl rand -hex 32
    JWT_SECRET_KEY: str = get_env_var("JWT_SECRET_KEY", "replace_this_with_a_real_secret_key_32_chars_long")
    JWT_ALGORITHM: str = get_env_var("JWT_ALGORITHM", "HS256")
    # Token validity period in minutes (1 day = 1440 minutes)
    # IMPORTANT: In .env files, don't include comments on the same line as values
    # BAD:  ACCESS_TOKEN_EXPIRE_MINUTES=1440 # 1 day
    # GOOD: ACCESS_TOKEN_EXPIRE_MINUTES=1440
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 1 day

    # --- Security Settings ---
    # Add any other security-related configs here, e.g., CORS origins
    # BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000"] # Example for frontend

    class Config:
        # This makes Pydantic load variables from a .env file
        # Note: pydantic-settings looks for .env by default if python-dotenv is installed
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True
        # Explicitly disable environment reading for problematic fields
        fields = {
            'ACCESS_TOKEN_EXPIRE_MINUTES': {
                'env': None,  # Disable environment reading for this field
            }
        }
        # Validate values during assignment
        validate_assignment = True

# Use lru_cache to cache the settings instance
@lru_cache()
def get_settings() -> Settings:
    # Add basic error handling
    try:
        settings = Settings()
        return settings
    except Exception as e:
        print(f"Error loading settings: {e}")
        # Provide more context if possible
        if isinstance(e, ValueError) and '.env' in str(e):
            print("Ensure .env file exists in the project root and contains DATABASE_URL and JWT_SECRET_KEY.")
        raise # Re-raise the exception after printing info

# Initialize settings early to catch missing env vars on startup
settings = get_settings() 