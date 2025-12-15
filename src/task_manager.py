import sqlite3

class TaskErrorManager(Exception):
    pass

class AuthenticationError(TaskErrorManager):
    """Error. Authentication Error"""
    def __init__(self, user_id):
        self.user_id = user_id
        super().__init__(f"Error de autenticatión. {user_id} no tiene permisos.")

class TaskNotFoundError(TaskErrorManager):
    """Error. Tarea no existe."""
    def __init__(self, task_id):
        self.task_id = task_id
        super().__init__(f"Error. Tarea con ID '{task_id}' no encontrada.")
    
class Task:
    def __init__(self, id, user_id, description, completed=False, due_date = None):
        self.id = id
        self.description = description
        self.completed = False
        self.due_date = due_date
        self.user_id = user_id
    
    def is_completed(self):
        return self.completed
    
    def get_description(self):
        return self.description

    def get_id(self):
        return self.id
    def get_due_date(self):
        return self.due_date
    
class TaskManager:
    #1. Constructor
    def __init__(self, repository):
        self.repository = repository
    #2. Creación y gestión de usuarios
    def add_user(self, user_str):
        return self.repository.add_user(user_str)
    
    def users_count(self):
        return self.repository.users_count()
    
    def contains_user(self, user_id):
        return self.repository.contains_user(user_id)
    
    #3. CRUD De Tareas
    #3.1 Create
    def add_task_by_user_id_global(self, description, user_id, due_date = None):
        
        return self.repository.add_task_by_user_id_global(description, user_id, due_date)
    #3.2 Read
    def get_task_by_id_global(self, task_id):
        self.assert_is_valid_task_id_global(task_id)
        return self.repository.get_task_by_id_global(task_id)

    def get_pending_tasks_by_user_id_global(self, user_id):
        return self.repository.get_pending_tasks_by_user_id_global(user_id)

    def get_overdue_tasks_by_user_id_global(self, user_id):
        return self.repository.get_overdue_tasks_by_user_id_global(user_id)

    #3.3 Update   
    def complete_task_global(self, task_id):
        self.assert_is_valid_task_id_global(task_id)
        self.repository.complete_task_global(task_id)

    def update_task_due_date_global(self, task_id, new_due_date):
        self.assert_is_valid_task_id_global(task_id)
        self.repository.update_task_due_date_global(task_id, new_due_date)
    
    def update_task_description_global(self, task_id, new_description):
        self.assert_is_valid_task_id_global(task_id)
        self.repository.update_task_description_global(task_id, new_description)
    #3.4 Delete
    def remove_task_due_date_global(self, task_id):
        self.assert_is_valid_task_id_global(task_id)
        self.repository.update_task_due_date_global(task_id, None)

    def delete_task_global(self, task_id):
        self.assert_is_valid_task_id_global(task_id)
        self.repository.delete_task_global(task_id)

    #4. State
    def task_is_completed(self, task_id):
        self.assert_is_valid_task_id_global(task_id)
        return self.repository.task_is_completed(task_id)
    
    def tasks_count_by_user_id(self, user_id):
        return self.repository.tasks_count_by_user_id(user_id)
    
    def contains_task_by_user_id(self, user_id, task_id):
        return self.repository.contains_task_by_user_id(user_id, task_id)
    
    #Assert methods
    def assert_is_valid_task_id_global(self, task_id):
        if not self.repository.contains_task_by_user_id(task_id):
            raise TaskNotFoundError(task_id)
    
    def assert_task_id_belongs_to_user(self, task_id, user_id):
        if not self.repository.contains_task_by_user_id(task_id, user_id):
            raise AuthenticationError(user_id)
    
    

    