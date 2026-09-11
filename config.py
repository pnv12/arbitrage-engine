from decimal import Decimal
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "ArbitrageEngine"
    DEBUG: bool = False
    
    # Торговые параметры
    MIN_PROFIT_THRESHOLD: Decimal = Decimal("0.005")  # 0.5%
    
    # Сетевые настройки и Circuit Breaker
    MAX_RECONNECT_ATTEMPTS: int = 5
    CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = 3
    CIRCUIT_BREAKER_RECOVERY_TIME: int = 30  # секунд
    MAX_CLOCK_DRIFT_MS: int = 1000  # Максимально допустимый рассинхрон времени в мс
    
    # Настройки очередей
    QUEUE_MAX_SIZE: int = 1000

    class Config:
        env_file = ".env"

settings = Settings()
