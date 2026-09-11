import pytest
import asyncio
from decimal import Decimal
from time import time

# Предполагается импорт ваших модулей:
# from engine.math import calculate_spread
# from engine.circuit_breaker import CircuitBreaker, CircuitOpenException
# from engine.queue import BoundedQueue

# --- 1. Тест Decimal Математики ---
def calculate_spread(bid: Decimal, ask: Decimal, fee_pct: Decimal) -> Decimal:
    """Вспомогательная функция расчета спреда с учетом комиссий."""
    if ask <= Decimal("0") or bid <= Decimal("0"):
        return Decimal("0")
    total_fee_multiplier = Decimal("1") - (fee_pct * Decimal("2"))
    profit = (bid * total_fee_multiplier) - ask
    return (profit / ask) * Decimal("100")

def test_decimal_precision():
    # Проверка отсутствия ошибок округления float (типа 0.1 + 0.2 != 0.3)
    ask = Decimal("100.00000001")
    bid = Decimal("101.50000000")
    fee = Decimal("0.001")  # 0.1%

    spread = calculate_spread(bid, ask, fee)
    
    assert isinstance(spread, Decimal)
    assert spread > Decimal("0")
    # Проверяем строгое соответствие
    expected = (((bid * Decimal("0.998")) - ask) / ask) * Decimal("100")
    assert spread == expected


# --- 2. Тест Circuit Breaker ---
class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, recovery_time: int = 2):
        self.failure_threshold = failure_threshold
        self.recovery_time = recovery_time
        self.failures = 0
        self.state = "CLOSED"
        self.last_state_change = time()

    def record_failure(self):
        self.failures += 1
        if self.failures >= self.failure_threshold:
            self.state = "OPEN"
            self.last_state_change = time()

    def record_success(self):
        self.failures = 0
        self.state = "CLOSED"

    def can_execute(self) -> bool:
        if self.state == "OPEN":
            if time() - self.last_state_change > self.recovery_time:
                self.state = "HALF-OPEN"
                return True
            return False
        return True

def test_circuit_breaker_states():
    cb = CircuitBreaker(failure_threshold=2, recovery_time=1)
    
    assert cb.can_execute() is True
    
    # Регистрируем ошибки
    cb.record_failure()
    assert cb.can_execute() is True
    
    cb.record_failure()  # Превышен порог -> OPEN
    assert cb.can_execute() is False
    
    # Эмулируем прохождение времени восстановления
    cb.last_state_change -= 2
    assert cb.can_execute() is True  # Переход в HALF-OPEN


# --- 3. Тест Backpressure в очереди ---
@pytest.mark.asyncio
async def test_bounded_queue_backpressure():
    queue = asyncio.Queue(maxsize=2)
    
    await queue.put("item1")
    await queue.put("item2")
    
    assert queue.full() is True
    
    # Проверяем, что попытка вставить без ожидания вызывает исключение (Backpressure trigger)
    with pytest.raises(asyncio.QueueFull):
        queue.put_nowait("item3")
  
