"""
Script to create a new .env file with correct formatting
"""
import os

def main():
    """
    Create a new .env file with correct settings
    """
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    print(f"Creating .env file at: {env_path}")
    
    env_content = """# Database Settings
DATABASE_URL=postgresql://user:password@localhost:5432/wellfixdb

# JWT Settings
JWT_SECRET_KEY=replace_this_with_a_real_secret_key_32_chars_long
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Optional: Security Settings
# BACKEND_CORS_ORIGINS=http://localhost:3000
"""
    
    try:
        with open(env_path, 'w') as f:
            f.write(env_content)
        print(".env file created successfully!")
    except Exception as e:
        print(f"Error creating .env file: {e}")

if __name__ == "__main__":
    main() 