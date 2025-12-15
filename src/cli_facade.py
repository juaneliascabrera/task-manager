from src.task_manager import *
class TaskManagerCliFacade:
    def __init__(self, manager: TaskManager):
        self.manager = manager
    
    #User handling
    def create_user(self, username):
        return self.manager.add_user(username)
    #Task creating
    def create_task(self, username, description, due_date = None):
        user_id = self.manager.get_user_id_by_username(username)
        return self.manager.add_task_for_user(description, user_id, due_date)
    #Task removing
    def delete_task(self, username, task_id):
        user_id = self.manager.get_user_id_by_username(username)
        return self.manager.delete_task_for_user(task_id, user_id)
    #Task completing
    def complete_task(self, username, task_id):
        user_id = self.manager.get_user_id_by_username(username)
        return self.manager.complete_task_for_user(task_id, user_id)
    #List pending tasks
    def list_pending_tasks(self, username):
        user_id = self.manager.get_user_id_by_username(username)
        return self.manager.get_pending_tasks_for_user(user_id)
    #Update
    def update_task_description(self, username, task_id, new_description):
        user_id = self.manager.get_user_id_by_username(username)
        return self.manager.update_task_description_for_user(task_id, new_description, user_id)
    
    def update_task_date(self, username, task_id, new_date):
        user_id = self.manager.get_user_id_by_username(username)
        return self.manager.update_task_overdue_date_for_user(task_id, new_date, user_id)
