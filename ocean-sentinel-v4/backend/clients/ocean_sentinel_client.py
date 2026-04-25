"""
Client HTTP résilient pour Ocean Sentinel API
Implémente: Circuit Breaker, Retry avec Full Jitter, Cache, Observabilité
"""
import httpx
import logging
import time
import random
import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
from functools import wraps
import json

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """États du Circuit Breaker"""
    CLOSED = 0      # Fonctionnement normal
    OPEN = 1        # Circuit ouvert (fail fast)
    HALF_OPEN = 2   # Test de récupération


@dataclass
class CircuitBreakerConfig:
    """Configuration Circuit Breaker"""
    failure_threshold: float = 0.5  # 50% échecs
    success_threshold: int = 5      # 5 succès pour fermer
    timeout_seconds: int = 10       # Durée état OPEN
    half_open_max_calls: int = 3    # Appels test en HALF_OPEN


@dataclass
class RetryConfig:
    """Configuration Retry avec Full Jitter"""
    max_attempts: int = 3
    base_delay_ms: int = 100
    max_delay_ms: int = 10000
    retry_on_status: List[int] = None
    
    def __post_init__(self):
        if self.retry_on_status is None:
            self.retry_on_status = [429, 500, 502, 503, 504]


class CircuitBreaker:
    """
    Implémentation Circuit Breaker Pattern
    Protège contre surcharge API externe
    """
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.half_open_calls = 0
    
    def call(self, func, *args, **kwargs):
        """Exécute fonction avec protection Circuit Breaker"""
        
        # État OPEN: Fail fast
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                self.half_open_calls = 0
                logger.info("Circuit Breaker: OPEN → HALF_OPEN")
            else:
                raise CircuitBreakerOpenError("Circuit breaker is OPEN")
        
        # État HALF_OPEN: Limiter appels test
        if self.state == CircuitState.HALF_OPEN:
            if self.half_open_calls >= self.config.half_open_max_calls:
                raise CircuitBreakerOpenError("Circuit breaker HALF_OPEN limit reached")
            self.half_open_calls += 1
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        """Gestion succès"""
        self.failure_count = 0
        
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitState.CLOSED
                self.success_count = 0
                logger.info("Circuit Breaker: HALF_OPEN → CLOSED")
    
    def _on_failure(self):
        """Gestion échec"""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            logger.warning("Circuit Breaker: HALF_OPEN → OPEN")
        elif self.state == CircuitState.CLOSED:
            # Vérifier seuil échecs
            if self.failure_count >= self.config.failure_threshold * 10:  # Sur 10 requêtes
                self.state = CircuitState.OPEN
                logger.error("Circuit Breaker: CLOSED → OPEN")
    
    def _should_attempt_reset(self) -> bool:
        """Vérifier si timeout OPEN expiré"""
        if self.last_failure_time is None:
            return True
        elapsed = (datetime.utcnow() - self.last_failure_time).total_seconds()
        return elapsed >= self.config.timeout_seconds


class CircuitBreakerOpenError(Exception):
    """Exception levée quand Circuit Breaker est ouvert"""
    pass


class SimpleCache:
    """Cache LRU simple pour Graceful Degradation"""
    
    def __init__(self, ttl_seconds: int = 300, max_size: int = 100):
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        self._cache: Dict[str, tuple[Any, datetime]] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Récupérer valeur du cache"""
        if key not in self._cache:
            return None
        
        value, timestamp = self._cache[key]
        if (datetime.utcnow() - timestamp).total_seconds() > self.ttl_seconds:
            del self._cache[key]
            return None
        
        return value
    
    def set(self, key: str, value: Any):
        """Stocker valeur dans cache"""
        if len(self._cache) >= self.max_size:
            # Supprimer entrée la plus ancienne (LRU simplifié)
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k][1])
            del self._cache[oldest_key]
        
        self._cache[key] = (value, datetime.utcnow())
    
    def clear(self):
        """Vider cache"""
        self._cache.clear()


class OceanSentinelClient:
    """
    Client HTTP résilient pour Ocean Sentinel API
    
    Features:
    - Circuit Breaker
    - Retry avec Full Jitter Backoff
    - Cache avec Graceful Degradation
    - Observabilité (logs structurés, métriques)
    - W3C Trace Context
    """
    
    def __init__(
        self,
        base_url: str = "https://oceansentinelle.fr/api/v1",
        timeout_seconds: int = 5,
        circuit_breaker_config: Optional[CircuitBreakerConfig] = None,
        retry_config: Optional[RetryConfig] = None,
        enable_cache: bool = True,
        cache_ttl_seconds: int = 300
    ):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout_seconds
        
        # Circuit Breaker
        self.circuit_breaker = CircuitBreaker(
            circuit_breaker_config or CircuitBreakerConfig()
        )
        
        # Retry config
        self.retry_config = retry_config or RetryConfig()
        
        # Cache
        self.cache_enabled = enable_cache
        self.cache = SimpleCache(ttl_seconds=cache_ttl_seconds) if enable_cache else None
        
        # HTTP Client
        self.client = httpx.Client(
            timeout=timeout_seconds,
            headers={
                "Accept": "application/json",
                "User-Agent": "OceanSentinel-Client/1.0.0"
            }
        )
    
    def _generate_trace_id(self) -> str:
        """Générer Trace ID (W3C Trace Context)"""
        return hashlib.sha256(
            f"{datetime.utcnow().isoformat()}{random.random()}".encode()
        ).hexdigest()[:32]
    
    def _calculate_backoff_delay(self, attempt: int) -> float:
        """
        Calcul délai backoff avec Full Jitter
        Formula: sleep = random(0, min(cap, base * 2^attempt))
        """
        max_delay = min(
            self.retry_config.max_delay_ms,
            self.retry_config.base_delay_ms * (2 ** attempt)
        )
        return random.uniform(0, max_delay) / 1000.0  # Convertir en secondes
    
    def _should_retry(self, status_code: int, attempt: int) -> bool:
        """Vérifier si retry nécessaire"""
        return (
            attempt < self.retry_config.max_attempts and
            status_code in self.retry_config.retry_on_status
        )
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        trace_id: str,
        **kwargs
    ) -> httpx.Response:
        """Exécuter requête HTTP avec retry"""
        url = f"{self.base_url}{endpoint}"
        headers = kwargs.pop('headers', {})
        headers['traceparent'] = f"00-{trace_id}-{random.randint(0, 2**64-1):016x}-01"
        
        for attempt in range(self.retry_config.max_attempts):
            try:
                start_time = time.time()
                
                response = self.client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    **kwargs
                )
                
                latency_ms = (time.time() - start_time) * 1000
                
                # Log structuré
                logger.info(
                    "HTTP request completed",
                    extra={
                        "trace_id": trace_id,
                        "method": method,
                        "url": url,
                        "status": response.status_code,
                        "latency_ms": round(latency_ms, 2),
                        "attempt": attempt + 1
                    }
                )
                
                # Vérifier si retry nécessaire
                if self._should_retry(response.status_code, attempt):
                    delay = self._calculate_backoff_delay(attempt)
                    logger.warning(
                        f"Retrying request after {delay:.2f}s",
                        extra={
                            "trace_id": trace_id,
                            "status": response.status_code,
                            "attempt": attempt + 1,
                            "delay_seconds": delay
                        }
                    )
                    time.sleep(delay)
                    continue
                
                response.raise_for_status()
                return response
                
            except httpx.TimeoutException as e:
                logger.error(
                    "Request timeout",
                    extra={
                        "trace_id": trace_id,
                        "url": url,
                        "attempt": attempt + 1,
                        "error": str(e)
                    }
                )
                if attempt < self.retry_config.max_attempts - 1:
                    delay = self._calculate_backoff_delay(attempt)
                    time.sleep(delay)
                else:
                    raise
            
            except httpx.HTTPStatusError as e:
                logger.error(
                    "HTTP error",
                    extra={
                        "trace_id": trace_id,
                        "url": url,
                        "status": e.response.status_code,
                        "attempt": attempt + 1
                    }
                )
                raise
        
        raise Exception(f"Max retries ({self.retry_config.max_attempts}) exceeded")
    
    def _get_with_cache(
        self,
        endpoint: str,
        cache_key: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """GET avec cache et Circuit Breaker"""
        trace_id = self._generate_trace_id()
        cache_key = cache_key or endpoint
        
        # Vérifier cache
        if self.cache_enabled and self.cache:
            cached = self.cache.get(cache_key)
            if cached:
                logger.info(f"Cache HIT: {cache_key}", extra={"trace_id": trace_id})
                return cached
        
        try:
            # Appel avec Circuit Breaker
            response = self.circuit_breaker.call(
                self._make_request,
                "GET",
                endpoint,
                trace_id,
                **kwargs
            )
            
            data = response.json()
            
            # Mettre en cache
            if self.cache_enabled and self.cache:
                self.cache.set(cache_key, data)
            
            return data
            
        except CircuitBreakerOpenError:
            logger.error(
                "Circuit breaker OPEN, using cache fallback",
                extra={"trace_id": trace_id, "endpoint": endpoint}
            )
            
            # Graceful Degradation: Retourner cache même périmé
            if self.cache_enabled and self.cache:
                cached = self.cache.get(cache_key)
                if cached:
                    return cached
            
            raise
    
    # === API Methods ===
    
    def health_check(self) -> Dict[str, Any]:
        """GET /health"""
        return self._get_with_cache("/health")
    
    def list_stations(self) -> Dict[str, Any]:
        """GET /api/v1/stations"""
        return self._get_with_cache("/stations")
    
    def get_station_latest(self, station_id: str) -> Dict[str, Any]:
        """GET /api/v1/station/{station_id}/latest"""
        if station_id not in ["BARAG_PROXY", "ARCACHON_EYRAC"]:
            raise ValueError(f"Invalid station_id: {station_id}")
        
        return self._get_with_cache(
            f"/station/{station_id}/latest",
            cache_key=f"station_{station_id}_latest"
        )
    
    def get_meteo_arcachon(self) -> Dict[str, Any]:
        """GET /api/v1/meteo/arcachon"""
        return self._get_with_cache("/meteo/arcachon")
    
    def close(self):
        """Fermer client HTTP"""
        self.client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# === Exemple d'utilisation ===

if __name__ == "__main__":
    # Configuration logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Créer client
    with OceanSentinelClient(
        base_url="https://oceansentinelle.fr/api/v1",
        timeout_seconds=5,
        enable_cache=True,
        cache_ttl_seconds=300
    ) as client:
        
        try:
            # Test health check
            health = client.health_check()
            print(f"✅ Health: {health['status']}")
            
            # Test liste stations
            stations = client.list_stations()
            print(f"✅ Stations: {stations['count']} trouvées")
            
            # Test données station
            barag = client.get_station_latest("BARAG_PROXY")
            print(f"✅ BARAG: {len(barag['parameters'])} paramètres")
            
            # Test météo
            meteo = client.get_meteo_arcachon()
            print(f"✅ Météo: {meteo['wind_speed']} km/h, {meteo['air_temp']}°C")
            
        except CircuitBreakerOpenError:
            print("❌ Circuit Breaker OPEN - API indisponible")
        except Exception as e:
            print(f"❌ Erreur: {e}")
