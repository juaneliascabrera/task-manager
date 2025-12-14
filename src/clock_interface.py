from abc import ABC, abstractmethod
from datetime import datetime

class AbstractClock(ABC):
    "Abstract interface for a clock"
    @abstractmethod
    def now(self) -> datetime:
        pass
    
    
