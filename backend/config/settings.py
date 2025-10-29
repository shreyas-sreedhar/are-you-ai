"""Application configuration using Pydantic Settings."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # NIM API Configuration
    nim_api_key: str
    nim_api_endpoint: str = "https://integrate.api.nvidia.com/v1/chat/completions"
    nim_model_name: str = "nvidia/nemotron-nano-12b-v2-vl"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # Image Processing Configuration
    max_frame_size: int = 1024
    confidence_threshold: float = 0.7
    
    # Frame Sequence Analysis Configuration
    frame_sequence_length: int = 5  # Analyze 5 consecutive frames
    frame_interval_ms: int = 200  # 200ms between frames
    min_inconsistencies: int = 2  # Need 2+ issues to flag as fake

    # News/Text Analysis Models (NIM)
    model_reason: str = "meta/llama-3.1-405b-instruct"
    model_fact: str = "nvidia/llama-3.1-nemotron-70b-instruct"
    model_extract: str = "meta/llama-3.1-70b-instruct"

    # Backend base URL (for internal client wrapper)
    backend_base_url: str = "http://localhost:8000"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "allow"  # Ignore extra fields from .env


# Global settings instance
settings = Settings()

