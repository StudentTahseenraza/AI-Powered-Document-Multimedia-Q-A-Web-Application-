# backend/app/config.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
env_file = Path(__file__).parent.parent / '.env'
if env_file.exists():
    load_dotenv(env_file)

class Settings:
    # MongoDB
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "ai_qa_db")
    
    # OpenRouter API
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "openai/gpt-3.5-turbo")
    
    # Hugging Face (for embeddings)
    HUGGINGFACE_API_KEY: str = os.getenv("HUGGINGFACE_API_KEY", "")
    HF_EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"  # Add this line
    
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
    ]

settings = Settings()

# Create upload directory
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

print("\n" + "="*50)
print("CONFIGURATION STATUS")
print("="*50)
print(f"OPENROUTER_API_KEY: {'✅ SET' if settings.OPENROUTER_API_KEY else '❌ NOT SET'}")
print(f"MONGODB_URL: {settings.MONGODB_URL[:30]}...")
print("="*50 + "\n")