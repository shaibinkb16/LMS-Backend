import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # MongoDB
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "lms_db")
    
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # OpenAI (keeping for backward compatibility)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Groq (new LLM provider)
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    
    # File Upload
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # CORS
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://localhost:5174",  # Vite preview port
        "http://127.0.0.1:4173",
        "http://127.0.0.1:4040",
        "https://artlms.netlify.app",
        "https://3b1497bf074b.ngrok-free.app",
    ]

settings = Settings() 