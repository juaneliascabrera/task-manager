import unittest
from src.task_manager import TaskManager, TaskNotFoundError, Task, AuthenticationError
from src.task_repository import TaskRepository

class TestCliFacade(unittest.TestCase):
    """Set-Up"""
    def setUp(self):
        pass



    """def test_can_not_mark_other_user_task_as_completed(self):
        #Agregamos la tarea del usuario
        created_task_id = self.manager.add_task_by_user_id(self.generic_task_description_one, user_id=self.user_id_one)
        #Asserts (el usuario 2 no debería poder)
        with self.assertRaises(AuthenticationError):
            self.manager.user_wants_to_complete_task(self.user_id_two, created_task_id)
        #No debería estar marcada como completada
        self.assertFalse(self.manager.task_is_completed(created_task_id))

    def test_can_not_delete_other_user_task(self):
        #Agregamos la tarea del usuario
        created_task_id = self.manager.add_task_by_user_id(self.generic_task_description_one, user_id=self.user_id_one)
        #Asserts (el usuario 2 no debería poder)
        with self.assertRaises(AuthenticationError):
            self.manager.user_wants_to_delete_task(self.user_id_two, created_task_id)
        #No debería estar marcada como eliminada.
        self.assertTrue(self.manager.contains_task_by_user_id(self.user_id_one, created_task_id))"""

if __name__ == '__main__':
    unittest.main()

