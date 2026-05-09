# backend/app/config.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Get the backend directory
backend_dir = Path(__file__).parent.parent
env_file = backend_dir / '.env'

# Load .env file
if env_file.exists():
    load_dotenv(env_file)
    print(f"✅ Loaded .env from {env_file}")
else:
    print(f"❌ .env file not found at {env_file}")

class Settings:
    # MongoDB
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "ai_qa_db")
    
    # Google Gemini
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GEMINI_MODEL: str = "gemini-1.5-flash"
    
    # JWT
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # File upload
    MAX_FILE_SIZE: int = 100 * 1024 * 1024
    UPLOAD_DIR: str = "uploads"
    ALLOWED_EXTENSIONS: list = [".pdf", ".mp3", ".mp4", ".wav", ".m4a", ".webm"]
    
    # CORS
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
    ]

settings = Settings()

# Create upload directory
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

# Print status
print("\n" + "="*50)
print("CONFIGURATION STATUS")
print("="*50)
print(f"GOOGLE_API_KEY: {'✅ SET' if settings.GOOGLE_API_KEY else '❌ NOT SET'}")
print(f"MONGODB_URL: {settings.MONGODB_URL[:30]}...")
print(f"JWT_SECRET_KEY: {'✅ SET' if settings.JWT_SECRET_KEY != 'your-secret-key' else '⚠️ USING DEFAULT'}")
print("="*50 + "\n")