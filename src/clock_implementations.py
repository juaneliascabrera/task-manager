from datetime import datetime, timedelta
from .clock_interface import AbstractClock

class SystemClock(AbstractClock):
    "Implementación de reloj real"
    def now(self) -> datetime:
        return datetime.now()
    
class MockClock(AbstractClock):
    "Implementación simulada para testear"
    def __init__(self, start_time):
        self._current_time = start_time

    def now(self) -> datetime:
        return self._current_time
    
    def advance_time(self, days: int = 0, hours: int = 0, minutes: int = 0):
        "Avanzamos"
        delta = timedelta(days=days,hours=hours,minutes=minutes)
        self._current_time += delta
    