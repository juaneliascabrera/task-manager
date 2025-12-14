from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from src.task_manager import Task

class AbstractRepository(ABC):
    "Abstract interface for a repository"
    @abstractmethod
    def _to_db_format(self, dt: Optional[datetime]) -> object:
        pass
    @abstractmethod
    def _from_db_format(self, db_value: object) -> Optional[datetime]:
        pass
    @abstractmethod
    def add_task(self, description:str, due_date:Optional[datetime]) -> int:
        pass
    @abstractmethod
    def get_task_by_id(self, task_id: int) -> Task:
        pass
    @abstractmethod
    def get_pending_tasks(self) -> list[Task]:
        pass
    @abstractmethod
    def get_overdue_tasks(self) -> list[Task]:
        pass
    @abstractmethod
    def contains_task(self, task_id: int) -> bool:
        pass
    @abstractmethod
    def complete_task(self, task_id: int):
        pass
    @abstractmethod
    def update_task_due_date(self, task_id: int, new_due_date: datetime):
        pass
    @abstractmethod
    def update_task_description(self, task_id: int, new_description: str):
        pass
    @abstractmethod
    def delete_task(self, task_id: int):
        pass
    @abstractmethod
    def tasks_count(self) -> int:
        pass
    @abstractmethod
    def task_is_completed(self, task_id: int) -> bool:
        pass

    
