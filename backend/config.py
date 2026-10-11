import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Sanskrit POS Annotation API"
    API_PREFIX: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "sanskrit_super_secret_jwt_key_2026_mtech_dissertation")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Database: SQLite for effortless local dev, PostgreSQL for production
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./sanskrit_pos.db")
    
    # Path to the 70% automatically annotated CSV
    # CRITICAL: Only the 70% portion is touched; 30% portion remains completely untouched
    DATASET_CSV_PATH: str = os.getenv(
        "DATASET_CSV_PATH",
        os.path.expanduser("~/Desktop/News Domain/sanskrit_pos_data_10k/70_percent/auto_pos.csv")
    )
    
    # CORS Origins allowed to communicate with this API
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ]
    
    # Approved Sanskrit Consortium POS Tag Inventory
    # N, NS, NV, KNV, SN, SNV, SNS, SAM, SAMY, SAMP, KP, UP, AVN, AVP, AVUP, SAMB, AVU, K, AKV, AB, AVC, DVI, A
    APPROVED_SANSKRIT_TAGS: List[str] = [
        "N", "NS", "NV", "KNV", "SN", "SNV", "SNS", 
        "SAM", "SAMY", "SAMP", "KP", "UP", "AVN", "AVP", 
        "AVUP", "SAMB", "AVU", "K", "AKV", "AB", "AVC", "DVI", "A"
    ]

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
