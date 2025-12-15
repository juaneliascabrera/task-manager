import unittest
import os
from src.task_manager import *
from src.cli_facade import *
from src.task_repository import TaskRepository
from src.clock_implementations import MockClock
from datetime import datetime, timedelta
class TestCliFacade(unittest.TestCase):
    """Set-Up"""
    DB_TEST_NAME = 'test_cli_facade.db'
    def setUp(self):
        #Mock Clock and Repository
        self.mock_clock = MockClock(datetime(2025, 12, 14, 17, 00, 00))
        self.repository = TaskRepository(self.DB_TEST_NAME, self.mock_clock, True)
        #Manager
        self.manager = TaskManager(self.repository)
        #Facade
        self.facade = TaskManagerCliFacade(self.manager)
        #Generic descriptions
        self.task_description_1 = "Buy bread and milk"
        #Generic usernames (text)
        self.username_one = "jelias1203"
        self.username_two = "jel191"
        #Users
        self.user_id_one = self.manager.add_user(self.username_one)
        self.user_id_two = self.manager.add_user(self.username_two)
    def tearDown(self):
        return super().tearDown()

    def test_facade_can_create_user_by_username(self):
        #Username
        username = "martin1951"
        user_id = self.facade.create_user(username)

        #Asserts
        self.assertEqual(self.manager.get_user_name_by_id(user_id), username)

    def test_facade_can_create_task_by_username(self):
        """Test the whole system: The facade takes the username, turns out to ID, and delegates
        to the TaskManager
        """
        #Call the Facade
        task_id = self.facade.create_task(self.username_one, self.task_description_1)
        #Asserts
        self.assertIsInstance(task_id, int)
        self.assertGreaterEqual(task_id, 0)

        self.assertEqual(self.manager.tasks_count_by_user_id(self.user_id_one), 1)

        task = self.manager.get_task_by_id_for_user(task_id, self.user_id_one)
        self.assertEqual(task.get_description(), self.task_description_1)

    def test_facade_cannot_create_task_for_nonexistent_username(self):
        unexistent_username = "whoamI"
        #Call the facade
        with self.assertRaises(UsernameNotFoundError):
            self.facade.create_task(unexistent_username, self.task_description_1)

        self.assertFalse(self.manager.contains_user_by_username(unexistent_username))
        self.assertFalse(self.manager.has_tasks())

    def test_facade_cannot_create_user_with_existing_username(self):
        #Call the facade
        with self.assertRaises(UsernameAlreadyExistsError):
            self.facade.create_user(self.username_one)

    ##Session tests

    def test_user_can_delete_his_tasks(self):
        #Agregamos una tarea
        task_id = self.facade.create_task(self.username_one, self.task_description_1)
        #Intentamos borrarla
        self.facade.delete_task(self.username_one, task_id)
        #Asserts
        self.assertFalse(self.manager.contains_task_by_user_id(self.user_id_one, task_id))
    def test_user_cannot_delete_other_users_task(self):
        #Agregamos la tarea del usuario
        user_one_task_id = self.facade.create_task(self.username_one, self.task_description_1)
        with self.assertRaises(AuthenticationError):
            self.facade.delete_task(self.username_two, user_one_task_id)
        #No debería estar marcada como eliminada.
        self.assertTrue(self.manager.contains_task_by_user_id(self.user_id_one, user_one_task_id))
    

    def test_can_mark_his_tasks_as_completed(self):
        #Agregamos una tarea
        task_id = self.facade.create_task(self.username_one, self.task_description_1)
        #Intentamos completarla
        self.facade.complete_task(self.username_one, task_id)
        #Asserts
        self.assertTrue(self.manager.task_is_completed_for_user(self.user_id_one, task_id))

    def test_can_not_mark_other_user_task_as_completed(self):
        #Agregamos la tarea del usuario
        created_task_id = self.facade.create_task(self.username_one, self.task_description_1)
        #Asserts (el usuario 2 no debería poder)
        with self.assertRaises(AuthenticationError):
            self.facade.complete_task(self.username_two, created_task_id)
        #No debería estar marcada como completada
        self.assertFalse(self.manager.task_is_completed_global(created_task_id))
    
    def test_user_can_list_his_pending_tasks(self):
        #Agregamos 2 tareas
        task_id_one = self.facade.create_task(self.username_one, self.task_description_1)
        task_id_two = self.facade.create_task(self.username_one, self.task_description_1)
        #Sólo completamos una
        self.facade.complete_task(self.username_one, task_id_one)
        #Vemos que podamos listar y esté solo la otra
        pending_tasks = self.facade.list_pending_tasks(self.username_one)
        #Asserts
        self.assertEqual(len(pending_tasks), 1)
        self.assertTrue(pending_tasks[0].get_id() == task_id_two)

    def test_user_can_modify_description_of_his_tasks(self):
        #La creamos
        task_id = self.facade.create_task(self.username_one, self.task_description_1)
        #La modificamos
        self.facade.update_task_description(self.username_one, task_id, "New description")
        #Assert
        self.assertEqual(self.manager.get_task_by_id_global(task_id).get_description(), "New description")

    def test_user_can_modify_date_of_his_tasks(self):
        #La creamos
        due_date_original = self.mock_clock.now() + timedelta(days = 3)
        task_id = self.facade.create_task(self.username_one, self.task_description_1, due_date_original)
        due_date_new = due_date_original + timedelta(days = 1)
        #La modificamos
        self.facade.update_task_date(self.username_one, task_id, due_date_new)
        #Assert
        self.assertEqual(self.manager.get_task_by_id_global(task_id).get_due_date(), due_date_new)

    def test_user_can_not_modify_description_of_other_user_tasks(self):
         #Agregamos la tarea del usuario
        created_task_id = self.facade.create_task(self.username_one, self.task_description_1)
        #Asserts (el usuario 2 no debería poder)
        with self.assertRaises(AuthenticationError):
            self.facade.update_task_description(self.username_two, created_task_id, "not!")
        #No debería haberse modificado
        self.assertEqual(self.manager.get_task_by_id_global(created_task_id).get_description(), self.task_description_1)
    
    def test_user_can_not_modify_date_of_other_user_tasks(self):
        #La creamos
        due_date_original = self.mock_clock.now() + timedelta(days = 3)
        task_id = self.facade.create_task(self.username_one, self.task_description_1, due_date_original)
        due_date_new = due_date_original + timedelta(days = 1)
        #Asserts (el usuario 2 no debería poder)
        with self.assertRaises(AuthenticationError):
            self.facade.update_task_date(self.username_two, task_id, due_date_new)
        #No debería haberse modificado
        self.assertEqual(self.manager.get_task_by_id_global(task_id).get_due_date(), due_date_original)


if __name__ == '__main__':
    unittest.main()

