"""
Configuration Backend Ocean Sentinel
Gestion variables environnement avec Pydantic Settings
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Configuration application"""
    
    # API Keys
    coast_hf_api_key: str = ""
    hub_eau_api_key: str = ""
    
    # URLs API externes
    coast_hf_api_url: str = "https://coasthf.fr/api/v1"
    hub_eau_api_url: str = "https://hubeau.eaufrance.fr/api/v1/qualite_eau_littoral"
    
    # CORS
    allowed_origins: str = "https://oceansentinelle.fr,http://localhost:5173"
    
    # Cache Redis
    redis_url: str = "redis://localhost:6379/0"
    cache_ttl: int = 300  # 5 minutes
    
    # Logs
    log_level: str = "INFO"
    
    # Timeout requêtes HTTP
    http_timeout: float = 10.0
    
    # Retry
    max_retries: int = 3
    retry_delay: float = 1.0
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def origins_list(self) -> List[str]:
        """Parse CORS origins"""
        return [origin.strip() for origin in self.allowed_origins.split(",")]


# Instance globale
settings = Settings()
