import sqlite3

class TaskErrorManager(Exception):
    pass

class AuthenticationError(TaskErrorManager):
    """Error. Authentication Error"""
    def __init__(self, user_id):
        self.user_id = user_id
        super().__init__(f"Error de autenticación. {user_id} no tiene permisos.")

class TaskNotFoundError(TaskErrorManager):
    """Error. Tarea no existe."""
    def __init__(self, task_id):
        self.task_id = task_id
        super().__init__(f"Error. Tarea con ID '{task_id}' no encontrada.")

class UserIdNotFoundError(TaskErrorManager):
    """Error. Usuario no existe."""
    def __init__(self, user_id):
        self.user_id = user_id
        super().__init__(f"Error. Usuario con ID '{user_id}' no encontrado.")

class UsernameNotFoundError(TaskErrorManager):
    """Error. Usuario no existe."""
    def __init__(self, username):
        self.username = username
        super().__init__(f"Error. Usuario con username '{username}' no encontrado.")


class UsernameAlreadyExistsError(TaskErrorManager):
    """Error. Invalid username."""
    def __init__(self, username):
        self.username = username
        super().__init__(f"Error. Usuario con username '{username}' ya existe.")
    
class Task:
    def __init__(self, id, user_id, description, completed=False, due_date = None, priority = False, recurrency = False, recurrency_days = 0):
        self.id = id
        self.description = description
        self.completed = completed
        self.priority = priority
        self.due_date = due_date
        self.user_id = user_id
        self.recurrency = recurrency
        self.recurrency_days = recurrency_days
    
    def is_completed(self):
        return self.completed
    
    def is_priority(self):
        return self.priority
    
    def is_recurrency(self):
        return self.recurrency
    

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

    def has_tasks(self):
        return self.repository.has_tasks()
    
    #2. Creación y gestión de usuarios
    def add_user(self, user_str):
        self.assert_username_do_not_exists(user_str)
        return self.repository.add_user(user_str)
    
    def users_count(self):
        return self.repository.users_count()
    
    def contains_user_by_id(self, user_id):
        return self.repository.contains_user_by_id(user_id)
    
    def contains_user_by_username(self, username):
        return self.repository.contains_user_by_username(username)

    def update_user_name_of(self, user_id, new_username):
        return self.repository.update_user_name_of(user_id, new_username)
    
    
    #3. CRUD De Tareas
    #3.1 Create
    def add_task_by_user_id_global(self, description, user_id, due_date = None, priority=False, recurrency=False, recurrency_days=0):
        return self.repository.add_task_by_user_id_global(description, user_id, due_date, priority, recurrency, recurrency_days)
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

    def change_task_priority_global(self, task_id):
        self.assert_is_valid_task_id_global(task_id)
        self.repository.change_task_priority_global(task_id)

    def change_task_recurrency_global(self, task_id):
        self.assert_is_valid_task_id_global(task_id)
        self.repository.change_task_recurrency_global(task_id)

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
    def task_is_completed_global(self, task_id):
        self.assert_is_valid_task_id_global(task_id)
        return self.repository.task_is_completed_global(task_id)
    
    def tasks_count_by_user_id(self, user_id):
        return self.repository.tasks_count_by_user_id(user_id)
    
    def contains_task_by_user_id(self, user_id, task_id):
        return self.repository.contains_task_by_user_id(user_id, task_id)


    #SECURE METHODS (API)
    def add_task_for_user(self, description, user_id, due_date = None, priority=False, recurrency = False, recurrency_days = 0):
        "Add task. Needs to valid user_id"
        self.assert_is_valid_user_id(user_id)
        return self.add_task_by_user_id_global(description, user_id, due_date, priority, recurrency, recurrency_days)

    def get_pending_tasks_for_user(self, user_id):
        "Returns pending tasks. Needs to valid user_id"
        self.assert_is_valid_user_id(user_id)
        return self.get_pending_tasks_by_user_id_global(user_id)

    def change_task_priority_for_user(self, user_id, task_id):
        self.assert_task_id_belongs_to_user(user_id, task_id)
        self.repository.change_task_priority_global(task_id)

    def change_task_recurrency_for_user(self, user_id, task_id):
        self.assert_task_id_belongs_to_user(user_id, task_id)
        self.repository.change_task_recurrency_global(task_id)

    def get_task_by_id_for_user(self, task_id, user_id):
        "Return a Task. Needs to valid task_id with user_id"
        self.assert_task_id_belongs_to_user(task_id, user_id)
        return self.get_task_by_id_global(task_id)

    def task_is_completed_for_user(self, task_id, user_id):
        "Checks if task is completed. Needs to valid task_id with user_id"
        self.assert_task_id_belongs_to_user(task_id, user_id)
        return self.task_is_completed_global(task_id)

    def update_task_description_for_user(self, task_id, new_description, user_id):
        "Modify task description. Needs to valid task_id with user_id"
        self.assert_task_id_belongs_to_user(task_id, user_id)
        return self.update_task_description_global(task_id, new_description)

    def complete_task_for_user(self, task_id, user_id):
        "Completes task. Needs to valid task_id with user_id"
        self.assert_task_id_belongs_to_user(task_id, user_id)
        return self.complete_task_global(task_id)

    def update_task_overdue_date_for_user(self, task_id, new_due_date, user_id):
        "Modify task date. Needs to valid task_id with user_id"
        self.assert_task_id_belongs_to_user(task_id, user_id)
        return self.update_task_due_date_global(task_id, new_due_date)

    def remove_task_due_date_for_user(self, task_id, user_id):
        "Remove task date. Needs to valid task_id with user_id"
        self.assert_task_id_belongs_to_user(task_id, user_id)
        return self.remove_task_due_date_global(task_id)
    
    def delete_task_for_user(self, task_id, user_id):
        "Remove task. Needs to valid task_id with user_id"
        self.assert_task_id_belongs_to_user(task_id, user_id)
        return self.delete_task_global(task_id)

    def get_user_name_by_id(self, user_id):
        self.assert_is_valid_user_id(user_id)
        return self.repository.get_user_name_by_id(user_id)
    
    def get_user_id_by_username(self, username):
        self.assert_username_exists(username)
        return self.repository.get_user_id_by_username(username)
    



    #Assert methods
    def assert_is_valid_task_id_global(self, task_id):
        if not self.repository.contains_task_by_user_id(task_id):
            raise TaskNotFoundError(task_id)
    
    def assert_is_valid_user_id(self, user_id):
        if not self.repository.contains_user_by_id(user_id):
            raise UserIdNotFoundError(user_id)

    def assert_task_id_belongs_to_user(self, task_id, user_id):
        if not self.repository.contains_task_by_user_id(task_id, user_id):
            raise AuthenticationError(user_id)
    
    def assert_username_do_not_exists(self, username):
        if self.repository.contains_user_by_username(username):
            raise UsernameAlreadyExistsError(username)
        
    def assert_username_exists(self, username):
        if not self.repository.contains_user_by_username(username):
            raise UsernameNotFoundError(username)