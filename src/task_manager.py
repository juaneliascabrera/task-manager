import sqlite3

class TaskErrorManager(Exception):
    pass

class TaskNotFoundError(TaskErrorManager):
    """Error. Tarea no existe."""
    def __init__(self, task_id):
        self.task_id = task_id
        super().__init__(f"Error. Tarea con ID '{task_id}' no encontrada.")
    
class Task:
    def __init__(self, id, description, completed=False, due_date = None):
        self.id = id
        self.description = description
        self.completed = False
        self.due_date = due_date
    
    def is_completed(self):
        return self.completed
    
    def get_description(self):
        return self.description

    def get_id(self):
        return self.id
    def get_due_date(self):
        return self.due_date
    
class TaskManager:

    def __init__(self, repository):
        self.repository = repository

    def add_task(self, description, due_date = None):
        #Llamamos al repositorio
        return self.repository.add_task(description, due_date)
        
    def delete_task(self, task_id):
        self.assert_is_valid_task_id(task_id)
        self.repository.delete_task(task_id)

    def get_task_by_id(self, task_id):
        self.assert_is_valid_task_id(task_id)
        return self.repository.get_task_by_id(task_id)

    def get_pending_tasks(self):
        return self.repository.get_pending_tasks()
        
    def complete_task(self, task_id):
        self.assert_is_valid_task_id(task_id)
        self.repository.complete_task(task_id)

    def contains_task(self, task_id):
        return self.repository.contains_task(task_id)
        
    def task_is_completed(self, task_id):
        self.assert_is_valid_task_id(task_id)
        return self.repository.task_is_completed(task_id)
    
    def tasks_count(self):
        return self.repository.tasks_count()
    
    def update_task_due_date(self, task_id, new_due_date):
        self.assert_is_valid_task_id(task_id)
        self.repository.update_task_due_date(task_id, new_due_date)

    def update_task_description(self, task_id, new_description):
        self.assert_is_valid_task_id(task_id)
        self.repository.update_task_description(task_id, new_description)

    def remove_task_due_date(self, task_id):
        self.assert_is_valid_task_id(task_id)
        self.repository.update_task_due_date(task_id, None)
    def get_overdue_tasks(self):
        return self.repository.get_overdue_tasks()
    #Assert methods
    def assert_is_valid_task_id(self, task_id):
        if not self.repository.contains_task(task_id):
            raise TaskNotFoundError(task_id)